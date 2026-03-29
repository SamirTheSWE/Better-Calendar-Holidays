from collections import defaultdict

from rapidfuzz.fuzz import partial_ratio, ratio, token_set_ratio

from domain.models import Holiday


def deduplicate_holidays(holidays: list[Holiday], *, threshold: int = 80) -> list[Holiday]:
    by_date: dict[str, list[Holiday]] = defaultdict(list)
    for holiday in holidays:
        by_date[holiday.date.isoformat()].append(holiday)

    deduped: list[Holiday] = []
    for grouped in by_date.values():
        consumed: set[int] = set()
        for index, item in enumerate(grouped):
            if index in consumed:
                continue

            cluster = [item]
            consumed.add(index)
            for nested_index, candidate in enumerate(grouped[index + 1 :], start=index + 1):
                if nested_index in consumed:
                    continue
                if _is_similar(item.name, candidate.name, threshold=threshold):
                    cluster.append(candidate)
                    consumed.add(nested_index)

            deduped.append(_canonical(cluster))

    return sorted(deduped, key=lambda x: (x.date, x.name))


def _is_similar(left: str, right: str, *, threshold: int) -> bool:
    left_value = _normalize(left)
    right_value = _normalize(right)
    score = max(
        int(ratio(left_value, right_value)),
        int(partial_ratio(left_value, right_value)),
        int(token_set_ratio(left_value, right_value)),
    )
    return score >= threshold


def _normalize(value: str) -> str:
    return " ".join(value.lower().replace("-", " ").split())


def _canonical(cluster: list[Holiday]) -> Holiday:
    canonical = min(
        cluster,
        key=lambda item: (
            0 if item.region_code else 1,
            0 if item.location.strip().lower() != item.country_name.strip().lower() else 1,
            len(item.name.strip()),
            item.name.lower(),
        ),
    )
    cleaned_name = " ".join(canonical.name.split())
    return Holiday(
        country_code=canonical.country_code,
        country_name=canonical.country_name,
        date=canonical.date,
        name=cleaned_name,
        location=canonical.location,
        region_code=canonical.region_code,
    )
