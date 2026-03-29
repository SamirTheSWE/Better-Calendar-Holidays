import { HolidayItem } from "../models/holiday.models";

export interface GroupedHolidaySection {
    key: string;
    label: string;
    items: HolidayItem[];
}

export function groupByMonthYear(items: HolidayItem[]): GroupedHolidaySection[] {
    const sorted = [...items].sort((left, right) => left.date.localeCompare(right.date));
    const groups = new Map<string, GroupedHolidaySection>();

    for (const item of sorted) {
        const [year, month] = item.date.split("-").map((value) => Number.parseInt(value, 10));
        if (!Number.isFinite(year) || !Number.isFinite(month)) {
            continue;
        }
        const key = `${year}-${String(month).padStart(2, "0")}`;
        const label = `${year} - ${new Date(year, month - 1, 1).toLocaleString("en-GB", {
            month: "long",
        })}`;
        const current = groups.get(key);
        if (current) {
            current.items.push(item);
        } else {
            groups.set(key, { key, label, items: [item] });
        }
    }

    return [...groups.values()];
}
