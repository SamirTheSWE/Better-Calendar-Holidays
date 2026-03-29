import { HttpClient, HttpParams } from "@angular/common/http";
import { Injectable, inject } from "@angular/core";
import { Observable, map } from "rxjs";

import {
    ApiEnvelope,
    CountriesResponse,
    HolidayPreviewResponse,
    RegionsResponse,
} from "../models/holiday.models";

@Injectable({ providedIn: "root" })
export class HolidayApiService {
    private readonly http = inject(HttpClient);
    private readonly apiPrefix = new URL("api", document.baseURI).toString();

    getCountries(): Observable<CountriesResponse> {
        return this.http
            .get<ApiEnvelope<CountriesResponse>>(`${this.apiPrefix}/countries`)
            .pipe(map((response) => response.detail));
    }

    getRegions(countryCode: string): Observable<RegionsResponse> {
        return this.http
            .get<ApiEnvelope<RegionsResponse>>(`${this.apiPrefix}/regions/${countryCode}`)
            .pipe(map((response) => response.detail));
    }

    getPreview(countryCode: string, region: string | null): Observable<HolidayPreviewResponse> {
        let params = new HttpParams();
        if (region) {
            params = params.set("region", region);
        }
        return this.http
            .get<ApiEnvelope<HolidayPreviewResponse>>(`${this.apiPrefix}/preview/${countryCode}`, {
                params,
            })
            .pipe(map((response) => response.detail));
    }
}
