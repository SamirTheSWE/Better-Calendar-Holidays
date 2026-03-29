import logging
from datetime import date

import httpx

from domain.errors import SourceUnavailableError
from domain.interfaces import CountryHolidaySource
from domain.models import Country, Holiday
from services.region_normalizer import (
    available_regions_for_country,
    build_holiday_location,
    normalize_region_code,
)

logger = logging.getLogger(__name__)


class NagerClient(CountryHolidaySource):
    def __init__(self, *, base_url: str, timeout_seconds: float) -> None:
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout_seconds

    async def list_countries(self) -> list[Country]:
        url = f"{self._base_url}/AvailableCountries"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                response = await client.get(url)
                response.raise_for_status()
        except httpx.HTTPError as exc:
            raise SourceUnavailableError("Nager countries endpoint is unavailable.") from exc

        payload = response.json()
        countries = [
            Country(code=item["countryCode"], name=item["name"])
            for item in payload
            if item.get("countryCode") and item.get("name")
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
        url = f"{self._base_url}/PublicHolidays/{year}/{country_code}"
        logger.debug("Fetching Nager holidays: %s %s", country_code, year)
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.get(url)
            response.raise_for_status()

        normalized_region = (
            normalize_region_code(country_code=country_code, region_code=region) if region else None
        )
        holidays: list[Holiday] = []
        for item in response.json():
            try:
                holiday = _parse_nager_item(
                    item=item,
                    country_code=country_code,
                    country_name=country_name,
                    normalized_region=normalized_region,
                )
            except (KeyError, ValueError, TypeError):
                logger.warning("Skipping malformed Nager holiday item: %r", item)
                continue
            if holiday is not None:
                holidays.append(holiday)

        logger.debug("Nager returned %d holidays for %s %s", len(holidays), country_code, year)
        return holidays


def _parse_nager_item(
    *,
    item: object,
    country_code: str,
    country_name: str,
    normalized_region: str | None,
) -> Holiday | None:
    if not isinstance(item, dict):
        return None

    name = item.get("localName") or item.get("name")
    if not name:
        return None

    counties = item.get("counties")
    normalized_counties: set[str] = set()
    if isinstance(counties, list):
        normalized_counties = {
            normalize_region_code(country_code=country_code, region_code=value)
            for value in counties
            if isinstance(value, str)
        }
    is_global = bool(item.get("global", False))

    if normalized_region:
        if not is_global and normalized_region not in normalized_counties:
            return None
        item_region_code = normalized_region if not is_global else None
    else:
        item_region_code = (
            next(iter(normalized_counties))
            if not is_global and len(normalized_counties) == 1
            else None
        )

    return Holiday(
        country_code=country_code,
        country_name=country_name,
        date=_parse_date(item["date"]),
        name=str(name),
        location=build_holiday_location(country_name=country_name, region_code=item_region_code),
        region_code=item_region_code,
    )


def _parse_date(value: object) -> date:
    return date.fromisoformat(str(value))
