from datetime import timedelta
from hashlib import sha256
from typing import cast

from icalendar import Calendar, Event

from domain.models import Holiday


def generate_ics(holidays: list[Holiday]) -> bytes:
    calendar = Calendar()  # type: ignore[no-untyped-call]
    calendar.add("prodid", "-//better-calendar-holidays//EN")
    calendar.add("version", "2.0")
    calendar.add("x-wr-calname", "Better Calendar Holidays")

    for holiday in sorted(holidays, key=lambda x: (x.date, x.name)):
        event = Event()  # type: ignore[no-untyped-call]
        event.add("uid", _stable_uid(holiday))
        event.add("summary", holiday.name)
        event.add("dtstart", holiday.date)
        event.add("dtend", holiday.date + timedelta(days=1))
        event.add("transp", "TRANSPARENT")
        event.add("location", holiday.location)
        calendar.add_component(event)

    return cast(bytes, calendar.to_ical())


def _stable_uid(holiday: Holiday) -> str:
    payload = (
        f"{holiday.country_code.upper()}|{(holiday.region_code or 'NATIONAL').upper()}|"
        f"{holiday.date.isoformat()}|{holiday.name.strip().lower()}"
    )
    digest = sha256(payload.encode("utf-8")).hexdigest()[:24]
    return f"{digest}@better-calendar-holidays"
