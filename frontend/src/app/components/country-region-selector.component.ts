import { CommonModule } from "@angular/common";
import { Component, EventEmitter, Input, Output } from "@angular/core";
import { FormsModule } from "@angular/forms";

import { CountryItem, RegionItem } from "../models/holiday.models";

@Component({
    selector: "app-country-region-selector",
    standalone: true,
    imports: [CommonModule, FormsModule],
    template: `
        <div class="field">
            <label for="country" class="field-label">Country</label>
            <select
                id="country"
                class="input-shell"
                [ngModel]="selectedCountry"
                (ngModelChange)="countryChanged.emit($event)"
            >
                <option value="">Select a country</option>
                <option
                    *ngFor="let country of countries; trackBy: trackByCode"
                    [value]="country.code"
                >
                    {{ country.name }} ({{ country.code }})
                </option>
            </select>
            <p class="field-error" *ngIf="countryError">{{ countryError }}</p>
        </div>

        <div class="field">
            <label for="region" class="field-label">Region (optional)</label>
            <select
                id="region"
                class="input-shell"
                [ngModel]="selectedRegion"
                (ngModelChange)="regionChanged.emit($event)"
                [disabled]="!selectedCountry || regions.length === 0"
            >
                <option value="">National (All Regions)</option>
                <option *ngFor="let region of regions; trackBy: trackByCode" [value]="region.code">
                    {{ region.name }} ({{ region.code }})
                </option>
            </select>
            <p class="field-error" *ngIf="regionError">{{ regionError }}</p>
        </div>
    `,
})
export class CountryRegionSelectorComponent {
    @Input() countries: CountryItem[] = [];
    @Input() regions: RegionItem[] = [];
    @Input() selectedCountry = "";
    @Input() selectedRegion = "";
    @Input() countryError = "";
    @Input() regionError = "";

    @Output() countryChanged = new EventEmitter<string>();
    @Output() regionChanged = new EventEmitter<string>();

    trackByCode(_index: number, item: CountryItem | RegionItem): string {
        return item.code;
    }
}
