import logging
from datetime import UTC, datetime

import httpx

from domain.errors import (
    BetterCalendarError,
    MissingCalendarificKeyError,
    SourceName,
    SourceUnavailableError,
)
from domain.interfaces import CountryHolidaySource, HolidayCache
from domain.models import Country, Holiday
from services.deduplicator import deduplicate_holidays
from services.region_normalizer import normalize_region_code
from services.registry import CountryRegistry

YEARS_IN_FEED = 2

logger = logging.getLogger(__name__)


class HolidayService:
    def __init__(
        self,
        *,
        sources: dict[SourceName, CountryHolidaySource],
        cache: HolidayCache,
        registry: CountryRegistry,
    ) -> None:
        self._sources = sources
        self._cache = cache
        self._registry = registry

    def list_countries(self) -> list[Country]:
        return self._registry.list_countries()

    async def list_regions(self, *, country_code: str) -> list[tuple[str, str]]:
        source_name = self._registry.source_for_country(country_code)
        source = self._select_source(source_name)
        return await source.list_regions(country_code.upper())

    async def holidays_for_feed(
        self,
        *,
        country_code: str,
        region: str | None = None,
    ) -> list[Holiday]:
        today = datetime.now(UTC).date()
        years = [today.year + offset for offset in range(YEARS_IN_FEED)]
        normalized_region = (
            normalize_region_code(country_code=country_code, region_code=region) if region else None
        )

        feed_items: list[Holiday] = []
        for year in years:
            year_holidays = await self._holidays_for_year(
                country_code=country_code,
                region=normalized_region,
                year=year,
            )
            feed_items.extend(year_holidays)

        return feed_items

    async def _holidays_for_year(
        self,
        *,
        country_code: str,
        region: str | None,
        year: int,
    ) -> list[Holiday]:
        country = self._registry.get_country(country_code)
        source_name = self._registry.source_for_country(country_code)
        source = self._select_source(source_name)

        cached = await self._cache.get(
            source=source_name,
            country_code=country_code,
            year=year,
            region=region,
        )
        if cached is not None:
            logger.debug("Cache hit: %s/%s/%s/%s", source_name.value, country_code, year, region)
            return cached

        logger.debug(
            "Cache miss, fetching: %s/%s/%s/%s", source_name.value, country_code, year, region
        )
        try:
            fetched = await source.fetch_holidays(
                country_code=country_code,
                country_name=country.name,
                year=year,
                region=region,
            )
            deduped = deduplicate_holidays(fetched)
            await self._cache.set(
                source=source_name,
                country_code=country_code,
                year=year,
                region=region,
                holidays=deduped,
            )
            return deduped
        except (httpx.HTTPError, ValueError, BetterCalendarError) as exc:
            logger.error("Failed to fetch %s/%s/%s: %s", country_code, year, region, exc)
            raise SourceUnavailableError(
                f"Could NOT Fetch Holidays for {country_code} from {source_name.value}"
            ) from exc

    def _select_source(self, source_name: SourceName) -> CountryHolidaySource:
        source = self._sources.get(source_name)
        if source is None:
            raise MissingCalendarificKeyError(
                "Calendarific API Key Is REQUIRED for This Country. "
                "Set CALENDARIFIC_API_KEY in backend/.env"
            )
        return source
