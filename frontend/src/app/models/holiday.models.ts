export interface CountryItem {
    code: string;
    name: string;
}

export interface ApiEnvelope<TDetail> {
    code: number;
    status: string;
    detail: TDetail;
}

export interface CountriesResponse {
    countries: CountryItem[];
}

export interface RegionItem {
    code: string;
    name: string;
}

export interface RegionsResponse {
    regions: RegionItem[];
}

export interface HolidayItem {
    date: string;
    name: string;
    location: string;
}

export interface HolidayPreviewResponse {
    holidays: HolidayItem[];
}
