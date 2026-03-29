from datetime import date
from typing import Any

from pydantic import BaseModel, Field


class ApiEnvelope(BaseModel):
    code: int
    status: str
    detail: dict[str, Any]


class CountryResponse(BaseModel):
    code: str = Field(min_length=2, max_length=2)
    name: str


class CountriesResponse(BaseModel):
    countries: list[CountryResponse]


class RegionResponse(BaseModel):
    code: str
    name: str


class RegionsResponse(BaseModel):
    country_code: str
    regions: list[RegionResponse]


class HolidayItem(BaseModel):
    date: date
    name: str
    location: str


class HolidayPreviewResponse(BaseModel):
    holidays: list[HolidayItem]
