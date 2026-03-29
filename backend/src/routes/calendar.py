from fastapi import APIRouter, Depends, Path, Query, Request, Response

from api.envelope import success_response
from api.schemas import ApiEnvelope, HolidayItem, HolidayPreviewResponse
from dependencies import get_service
from rate_limit import limiter
from routes.errors import raise_mapped_http_exception
from services.holiday_service import HolidayService
from services.ics_generator import generate_ics

router = APIRouter()


@router.get("/preview/{country_code}", response_model=ApiEnvelope)
@limiter.limit("30/minute")
async def preview(
    request: Request,
    country_code: str = Path(min_length=2, max_length=2),
    region: str | None = Query(default=None),
    service: HolidayService = Depends(get_service),
) -> dict[str, object]:
    try:
        holidays = await service.holidays_for_feed(country_code=country_code.upper(), region=region)
    except Exception as exc:
        raise_mapped_http_exception(
            exc=exc,
            country_code=country_code,
        )

    payload = HolidayPreviewResponse(
        holidays=[
            HolidayItem(date=item.date, name=item.name, location=item.location) for item in holidays
        ],
    ).model_dump()
    return success_response(status="Holiday Preview Retrieved", detail=payload)


@router.get("/calendar.ics")
@limiter.limit("20/minute")
async def calendar_feed(
    request: Request,
    country: str = Query(min_length=2, max_length=2),
    region: str | None = Query(default=None),
    service: HolidayService = Depends(get_service),
) -> Response:
    try:
        holidays = await service.holidays_for_feed(country_code=country.upper(), region=region)
    except Exception as exc:
        raise_mapped_http_exception(
            exc=exc,
            country_code=country,
        )

    payload = generate_ics(holidays)
    return Response(content=payload, media_type="text/calendar")
