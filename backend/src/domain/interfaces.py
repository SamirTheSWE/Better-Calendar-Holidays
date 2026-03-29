from typing import Protocol

from domain.errors import SourceName
from domain.models import Country, Holiday


class HolidaySource(Protocol):
    async def fetch_holidays(
        self,
        *,
        country_code: str,
        country_name: str,
        year: int,
        region: str | None,
    ) -> list[Holiday]: ...


class CountryProvider(Protocol):
    async def list_countries(self) -> list[Country]: ...

    async def list_regions(self, country_code: str) -> list[tuple[str, str]]: ...


class CountryHolidaySource(HolidaySource, CountryProvider, Protocol):
    pass


class HolidayCache(Protocol):
    async def get(
        self,
        *,
        source: SourceName,
        country_code: str,
        year: int,
        region: str | None,
    ) -> list[Holiday] | None: ...

    async def set(
        self,
        *,
        source: SourceName,
        country_code: str,
        year: int,
        region: str | None,
        holidays: list[Holiday],
    ) -> None: ...
