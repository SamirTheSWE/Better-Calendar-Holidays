import logging
from collections.abc import Mapping
from datetime import date
from typing import Any, cast

import httpx

from domain.interfaces import CountryHolidaySource
from domain.models import Country, Holiday
from services.region_normalizer import (
    available_regions_for_country,
    build_holiday_location,
    normalize_region_code,
)

logger = logging.getLogger(__name__)


class CalendarificClient(CountryHolidaySource):
    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout_seconds: float,
    ) -> None:
        self._api_key = api_key
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    async def list_countries(self) -> list[Country]:
        params = {"api_key": self._api_key}
        payload = await self._get_json(path="/countries", params=params)
        response_payload = self._response_object(payload, endpoint="countries")
        countries_payload = response_payload.get("countries", [])
        if not isinstance(countries_payload, list):
            raise ValueError("Invalid countries payload from Calendarific")

        countries = [
            Country(code=item["iso-3166"], name=item["country_name"])
            for item in countries_payload
            if isinstance(item, dict) and item.get("iso-3166") and item.get("country_name")
        ]
        return sorted(countries, key=lambda x: x.name)

    async def list_regions(self, country_code: str) -> list[tuple[str, str]]:
        return available_regions_for_country(country_code=country_code)

    async def fetch_holidays(
        self,
        *,
        country_code: str,
        country_name: str,
        year: int,
        region: str | None,
    ) -> list[Holiday]:
        normalized_region = (
            normalize_region_code(country_code=country_code, region_code=region) if region else None
        )
        params: dict[str, str | int] = {
            "api_key": self._api_key,
            "country": country_code,
            "year": year,
            "type": "national,local,religious",
        }
        if normalized_region:
            params["location"] = normalized_region.lower()

        logger.debug("Fetching Calendarific holidays: %s %s", country_code, year)
        payload = await self._get_json(path="/holidays", params=params)
        response_payload = self._response_object(payload, endpoint="holidays")
        holidays_payload = response_payload.get("holidays", [])
        if not isinstance(holidays_payload, list):
            raise ValueError("Invalid holidays payload from Calendarific")

        holidays: list[Holiday] = []
        for item in holidays_payload:
            if not isinstance(item, dict):
                continue
            name = item.get("name")
            date_payload = item.get("date")
            iso_date = date_payload.get("iso") if isinstance(date_payload, dict) else None
            if not name or not iso_date:
                continue
            holidays.append(
                Holiday(
                    country_code=country_code,
                    country_name=country_name,
                    date=date.fromisoformat(iso_date[:10]),
                    name=name,
                    location=build_holiday_location(
                        country_name=country_name, region_code=normalized_region
                    ),
                    region_code=normalized_region,
                )
            )

        logger.debug(
            "Calendarific returned %d holidays for %s %s", len(holidays), country_code, year
        )
        return holidays

    async def _get_json(
        self,
        *,
        path: str,
        params: Mapping[str, str | int],
    ) -> dict[str, Any]:
        url = f"{self._base_url}{path}"
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
        return cast(dict[str, Any], response.json())

    def _response_object(self, payload: dict[str, Any], *, endpoint: str) -> dict[str, Any]:
        response_payload = payload.get("response")
        if isinstance(response_payload, dict):
            return response_payload
        raise ValueError(f"Invalid response payload from Calendarific ({endpoint})")
