import { HttpErrorResponse } from "@angular/common/http";
import { Component, DestroyRef, OnInit, inject } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { Subject, of } from "rxjs";
import { catchError, distinctUntilChanged, switchMap, tap } from "rxjs/operators";

import { CountryRegionSelectorComponent } from "../components/country-region-selector.component";
import { ErrorPageComponent } from "../components/error-page.component";
import { HolidayPreviewComponent } from "../components/holiday-preview.component";
import { IcsUrlOutputComponent, LoadedUrl } from "../components/ics-url-output.component";
import { CountryItem, HolidayItem, RegionItem } from "../models/holiday.models";
import { HolidayApiService } from "../services/holiday-api.service";
import { GroupedHolidaySection, groupByMonthYear } from "../utils/holiday-grouping";

interface PreviewSelection {
    country: string;
    region: string | null;
}

@Component({
    selector: "app-home",
    standalone: true,
    imports: [
        CountryRegionSelectorComponent,
        ErrorPageComponent,
        HolidayPreviewComponent,
        IcsUrlOutputComponent,
    ],
    template: `
        @if (countryFetchFailed) {
            <app-error-page
                code="500"
                title="Service Unavailable"
                message="We couldn't load holiday data. Please try again later."
                [showRetry]="true"
                (retryClicked)="retryFetchCountries()"
            />
        } @else if (!loadingCountries) {
            <section class="surface-panel page-header">
                <p class="eyebrow">Better Calendar Holidays</p>
                <h1 class="page-title">Generate a country holiday ICS feed in seconds</h1>
                <p class="page-description">
                    Choose a country, copy your calendar URL, and subscribe once in your calendar
                    app.
                </p>
            </section>

            <div class="layout-grid">
                <div class="left-column">
                    <section class="surface-panel config-panel">
                        <h2 class="panel-title">Configuration</h2>
                        <p class="panel-subtitle">
                            Select a country or paste an existing ICS URL to load a saved config.
                        </p>

                        <div class="config-scroll">
                            <app-country-region-selector
                                [countries]="countries"
                                [regions]="regions"
                                [selectedCountry]="selectedCountry"
                                [selectedRegion]="selectedRegion"
                                [countryError]="countryError"
                                [regionError]="regionError"
                                (countryChanged)="onCountryChanged($event)"
                                (regionChanged)="onRegionChanged($event)"
                            />

                            <app-ics-url-output
                                [availableCountryCodes]="availableCountryCodes"
                                (urlLoaded)="onUrlLoaded($event)"
                            />
                        </div>
                    </section>
                </div>

                <div class="preview-column">
                    <app-holiday-preview
                        [groupedHolidays]="groupedHolidays"
                        [holidays]="holidays"
                        [loading]="loadingPreview"
                        [error]="previewError"
                        [icsUrl]="icsUrl"
                    />
                </div>
            </div>
        }
    `,
})
export class HomeComponent implements OnInit {
    private readonly api = inject(HolidayApiService);
    private readonly destroyRef = inject(DestroyRef);
    private readonly previewSelection$ = new Subject<PreviewSelection>();

    countries: CountryItem[] = [];
    regions: RegionItem[] = [];
    holidays: HolidayItem[] = [];
    groupedHolidays: GroupedHolidaySection[] = [];

    selectedCountry = "";
    selectedRegion = "";

    loadingCountries = true;
    loadingRegions = false;
    loadingPreview = false;

    countryError = "";
    regionError = "";
    previewError = "";

    countryFetchFailed = false;

    ngOnInit(): void {
        this.bindPreviewFetch();
        this.fetchCountries();
    }

    get icsUrl(): string {
        if (!this.selectedCountry) {
            return "";
        }
        const url = new URL("api/calendar.ics", document.baseURI);
        url.searchParams.set("country", this.selectedCountry);
        if (this.selectedRegion) {
            url.searchParams.set("region", this.selectedRegion);
        }
        return url.toString();
    }

    get availableCountryCodes(): string[] {
        return this.countries.map((c) => c.code.toUpperCase());
    }

    onCountryChanged(country: string): void {
        this.selectedCountry = country;
        this.selectedRegion = "";
        this.regionError = "";

        if (!country) {
            this.holidays = [];
            this.groupedHolidays = [];
            this.previewError = "";
            this.loadingPreview = false;
            this.regions = [];
            return;
        }

        this.fetchRegions();
        this.triggerPreviewFetch();
    }

    onRegionChanged(region: string): void {
        this.selectedRegion = region;
        if (!this.selectedCountry) {
            return;
        }
        this.triggerPreviewFetch();
    }

    onUrlLoaded({ country, region }: LoadedUrl): void {
        this.onCountryChanged(country);
        if (region) {
            this.selectedRegion = region;
            this.triggerPreviewFetch();
        }
    }

    retryFetchCountries(): void {
        this.countryFetchFailed = false;
        this.fetchCountries();
    }

    private fetchCountries(): void {
        this.loadingCountries = true;
        this.countryError = "";

        this.api
            .getCountries()
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: ({ countries }) => {
                    this.countries = countries;
                },
                error: (error: HttpErrorResponse) => {
                    this.countryFetchFailed = true;
                    this.countryError = this.errorMessage(error, "Could NOT Load Countries.");
                    this.loadingCountries = false;
                },
                complete: () => {
                    this.loadingCountries = false;
                },
            });
    }

    private fetchRegions(): void {
        this.loadingRegions = true;
        this.regionError = "";

        this.api
            .getRegions(this.selectedCountry)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe({
                next: ({ regions }) => {
                    this.regions = regions;
                    if (
                        this.selectedRegion &&
                        !regions.some((item) => item.code === this.selectedRegion)
                    ) {
                        this.selectedRegion = "";
                    }
                },
                error: (error: HttpErrorResponse) => {
                    this.regionError = this.errorMessage(error, "Could NOT Load Regions.");
                    this.regions = [];
                    this.selectedRegion = "";
                },
                complete: () => {
                    this.loadingRegions = false;
                },
            });
    }

    private bindPreviewFetch(): void {
        this.previewSelection$
            .pipe(
                distinctUntilChanged(
                    (left, right) => left.country === right.country && left.region === right.region,
                ),
                tap(() => {
                    this.loadingPreview = true;
                    this.previewError = "";
                }),
                switchMap((selection) =>
                    this.api.getPreview(selection.country, selection.region).pipe(
                        catchError((error: HttpErrorResponse) => {
                            this.previewError = this.errorMessage(
                                error,
                                "Could NOT Load Holiday Preview.",
                            );
                            this.holidays = [];
                            this.groupedHolidays = [];
                            return of(null);
                        }),
                    ),
                ),
                takeUntilDestroyed(this.destroyRef),
            )
            .subscribe((payload) => {
                this.loadingPreview = false;
                if (payload === null) {
                    return;
                }
                this.holidays = payload.holidays;
                this.groupedHolidays = groupByMonthYear(payload.holidays);
            });
    }

    private errorMessage(error: HttpErrorResponse, fallback: string): string {
        if (typeof error.error?.detail?.message === "string") {
            return error.error.detail.message;
        }
        if (typeof error.error?.status === "string") {
            return error.error.status;
        }
        return fallback;
    }

    private triggerPreviewFetch(): void {
        this.previewSelection$.next({
            country: this.selectedCountry,
            region: this.selectedRegion || null,
        });
    }
}
