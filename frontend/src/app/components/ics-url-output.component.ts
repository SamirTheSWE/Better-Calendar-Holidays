import { CommonModule } from "@angular/common";
import { Component, DestroyRef, EventEmitter, Input, Output, inject } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { FormsModule } from "@angular/forms";
import { timer } from "rxjs";

export interface LoadedUrl {
    country: string;
    region: string;
}

@Component({
    selector: "app-ics-url-output",
    standalone: true,
    imports: [CommonModule, FormsModule],
    template: `
        <div class="field">
            <label for="existing-url" class="field-label">Load existing ICS URL</label>
            <div class="inline-action-row">
                <input
                    id="existing-url"
                    class="input-shell action-input"
                    [(ngModel)]="existingIcsUrl"
                    placeholder="Paste a previously generated ICS URL"
                />
                <button
                    type="button"
                    class="btn-secondary action-button"
                    (click)="applyExistingUrl()"
                >
                    Apply
                </button>
            </div>
            <p class="hint-tooltip" *ngIf="loadUrlHint">{{ loadUrlHint }}</p>
            <p class="field-info" *ngIf="loadUrlStatus">{{ loadUrlStatus }}</p>
        </div>
    `,
})
export class IcsUrlOutputComponent {
    private readonly destroyRef = inject(DestroyRef);

    @Input() availableCountryCodes: string[] = [];

    @Output() urlLoaded = new EventEmitter<LoadedUrl>();

    existingIcsUrl = "";
    loadUrlHint = "";
    loadUrlStatus = "";

    applyExistingUrl(): void {
        this.loadUrlHint = "";
        this.loadUrlStatus = "";

        const rawValue = this.existingIcsUrl.trim();
        if (!rawValue) {
            this.showLoadHint("Enter a generated ICS URL first.");
            return;
        }

        let parsedUrl: URL;
        try {
            parsedUrl = new URL(rawValue);
        } catch {
            this.showLoadHint("URL is invalid.");
            return;
        }

        const country = parsedUrl.searchParams.get("country")?.trim().toUpperCase();
        if (!country || country.length !== 2) {
            this.showLoadHint("URL is missing a valid country code.");
            return;
        }

        if (!this.availableCountryCodes.includes(country)) {
            this.showLoadHint(`Country ${country} is not available in this environment.`);
            return;
        }

        const region = parsedUrl.searchParams.get("region")?.trim().toUpperCase() ?? "";
        this.loadUrlStatus = region
            ? `Loaded country ${country} and region ${region} from URL.`
            : `Loaded country ${country} from URL.`;
        this.urlLoaded.emit({ country, region });
    }

    private showLoadHint(message: string): void {
        this.loadUrlHint = message;
        timer(3500)
            .pipe(takeUntilDestroyed(this.destroyRef))
            .subscribe(() => {
                this.loadUrlHint = "";
            });
    }
}
