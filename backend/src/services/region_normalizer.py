import pycountry


def normalize_region_code(*, country_code: str, region_code: str) -> str:
    value = region_code.strip().upper().replace("_", "-")
    if not value:
        return ""
    if "-" not in value:
        return f"{country_code.upper()}-{value}"
    return value


def region_name(*, normalized_region_code: str) -> str:
    subdivision = pycountry.subdivisions.get(  # type: ignore[no-untyped-call]
        code=normalized_region_code
    )
    if subdivision is None:
        return normalized_region_code
    return str(subdivision.name)


def available_regions_for_country(*, country_code: str) -> list[tuple[str, str]]:
    country = country_code.upper()
    subdivisions = pycountry.subdivisions.get(country_code=country)  # type: ignore[no-untyped-call]
    if not subdivisions:
        return []

    items = sorted(
        ((str(item.code).upper(), str(item.name)) for item in subdivisions),
        key=lambda item: (item[1], item[0]),
    )
    return items


def build_holiday_location(*, country_name: str, region_code: str | None) -> str:
    if region_code:
        return f"{region_name(normalized_region_code=region_code)}, {country_name}"
    return country_name
