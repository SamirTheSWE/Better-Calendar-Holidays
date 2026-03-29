import logging

from redis.exceptions import RedisError

from domain.interfaces import CountryHolidaySource
from domain.models import Country, Holiday
from infrastructure.quota import CalendarificQuota

logger = logging.getLogger(__name__)


class QuotaGatedSource(CountryHolidaySource):
    """Wraps a CountryHolidaySource and enforces a Calendarific monthly quota."""

    def __init__(self, *, source: CountryHolidaySource, quota: CalendarificQuota) -> None:
        self._source = source
        self._quota = quota

    async def list_countries(self) -> list[Country]:
        await self._consume_or_raise()
        return await self._source.list_countries()

    async def list_regions(self, country_code: str) -> list[tuple[str, str]]:
        return await self._source.list_regions(country_code)

    async def fetch_holidays(
        self,
        *,
        country_code: str,
        country_name: str,
        year: int,
        region: str | None,
    ) -> list[Holiday]:
        await self._consume_or_raise()
        return await self._source.fetch_holidays(
            country_code=country_code,
            country_name=country_name,
            year=year,
            region=region,
        )

    async def _consume_or_raise(self) -> None:
        try:
            consumed = await self._quota.try_consume()
        except RedisError as exc:
            raise ValueError("Calendarific quota storage unavailable") from exc

        if not consumed:
            logger.warning("Calendarific quota exhausted")
            await self._quota.raise_if_exhausted()
