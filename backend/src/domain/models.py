from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class Holiday:
    country_code: str
    country_name: str
    date: date
    name: str
    location: str
    region_code: str | None = None


@dataclass(frozen=True)
class Country:
    code: str
    name: str
