from domain.errors import SourceName
from domain.models import Country


class CountryRegistry:
    def __init__(
        self,
        *,
        countries: list[Country],
        nager_country_codes: set[str],
        calendarific_country_codes: set[str],
    ) -> None:
        self._countries = countries
        self._by_code = {country.code.upper(): country for country in countries}
        self._nager_country_codes = nager_country_codes
        self._calendarific_country_codes = calendarific_country_codes

    @classmethod
    async def build(
        cls,
        *,
        nager_countries: list[Country],
        calendarific_countries: list[Country],
    ) -> "CountryRegistry":
        by_code: dict[str, Country] = {}
        for country in [*nager_countries, *calendarific_countries]:
            by_code[country.code.upper()] = country
        return cls(
            countries=sorted(by_code.values(), key=lambda x: x.name),
            nager_country_codes={country.code.upper() for country in nager_countries},
            calendarific_country_codes={country.code.upper() for country in calendarific_countries},
        )

    def list_countries(self) -> list[Country]:
        return self._countries

    def get_country(self, code: str) -> Country:
        country = self._by_code.get(code.upper())
        if country is None:
            raise KeyError(code)
        return country

    def source_for_country(self, code: str) -> SourceName:
        code_upper = code.upper()
        if code_upper in self._nager_country_codes:
            return SourceName.NAGER
        if code_upper in self._calendarific_country_codes:
            return SourceName.CALENDARIFIC
        raise KeyError(code)
