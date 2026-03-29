from fastapi import APIRouter, Depends, Path

from api.envelope import success_response
from api.schemas import (
    ApiEnvelope,
    CountriesResponse,
    CountryResponse,
    RegionResponse,
    RegionsResponse,
)
from dependencies import get_service
from routes.errors import raise_mapped_http_exception
from services.holiday_service import HolidayService

router = APIRouter()


@router.get("/health", response_model=ApiEnvelope)
async def health() -> dict[str, object]:
    return success_response(status="OK", detail={"service": "ok"})


@router.get("/countries", response_model=ApiEnvelope)
async def countries(service: HolidayService = Depends(get_service)) -> dict[str, object]:
    items = [
        CountryResponse(code=country.code, name=country.name)
        for country in service.list_countries()
    ]
    payload = CountriesResponse(countries=items).model_dump()
    return success_response(status="Countries Retrieved", detail=payload)


@router.get("/regions/{country_code}", response_model=ApiEnvelope)
async def regions(
    country_code: str = Path(min_length=2, max_length=2),
    service: HolidayService = Depends(get_service),
) -> dict[str, object]:
    try:
        items = await service.list_regions(country_code=country_code.upper())
    except Exception as exc:
        raise_mapped_http_exception(
            exc=exc,
            country_code=country_code,
        )

    payload = RegionsResponse(
        country_code=country_code.upper(),
        regions=[RegionResponse(code=code, name=name) for code, name in items],
    ).model_dump()
    return success_response(status="Regions Retrieved", detail=payload)
