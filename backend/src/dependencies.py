from fastapi import HTTPException, Request

from services.holiday_service import HolidayService


def get_service(request: Request) -> HolidayService:
    service: HolidayService | None = getattr(request.app.state, "service", None)
    if service is None:
        raise HTTPException(
            status_code=500,
            detail={
                "status": "Service Unavailable",
                "message": "Service failed to initialise. Check server logs.",
            },
        )
    return service
