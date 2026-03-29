from enum import StrEnum


class SourceName(StrEnum):
    NAGER = "nager"
    CALENDARIFIC = "calendarific"


class BetterCalendarError(Exception):
    """Base application error."""


class SourceUnavailableError(BetterCalendarError):
    """Raised when neither source nor cache is available."""


class MissingCalendarificKeyError(BetterCalendarError):
    """Raised when Calendarific is required but API key is not configured."""


class CalendarificQuotaExceededError(BetterCalendarError):
    """Raised when local Calendarific monthly quota is exhausted."""

    def __init__(self, *, used: int, limit: int, month_utc: str) -> None:
        self.used = used
        self.limit = limit
        self.month_utc = month_utc
        super().__init__(
            "Calendarific monthly quota reached. Try again next month or increase quota."
        )
