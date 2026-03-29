import { CommonModule } from "@angular/common";
import { Component, DestroyRef, Input, OnChanges, inject } from "@angular/core";
import { takeUntilDestroyed } from "@angular/core/rxjs-interop";
import { timer } from "rxjs";

import { HolidayItem } from "../models/holiday.models";
import { GroupedHolidaySection } from "../utils/holiday-grouping";
import {
    CopyInstructionsModalComponent,
    INSTRUCTION_CONFIGS,
} from "./copy-instructions-modal.component";

@Component({
    selector: "app-holiday-preview",
    standalone: true,
    imports: [CommonModule, CopyInstructionsModalComponent],
    template: `
        <section class="surface-panel preview-panel">
            <div class="preview-head">
                <h2 class="panel-title preview-title">Holiday Preview</h2>
                <div class="preview-head-right">
                    <p class="preview-loading" [class.is-visible]="loading">Updating...</p>
                    <button
                        type="button"
                        class="btn-primary action-button"
                        (click)="copyUrl()"
                        [disabled]="!icsUrl"
                    >
                        Copy URL
                    </button>
                </div>
            </div>
            <p class="hint-tooltip" *ngIf="copyHint">{{ copyHint }}</p>

            <p class="field-error" *ngIf="error">{{ error }}</p>

            <div class="preview-scroll">
                <ul class="event-list" *ngIf="!error && groupedHolidays.length > 0">
                    <ng-container *ngFor="let group of groupedHolidays; trackBy: trackByGroup">
                        <li class="month-header">{{ group.label }}</li>
                        <li
                            *ngFor="let holiday of group.items; trackBy: trackByHoliday"
                            class="event-row"
                        >
                            <div class="event-date-col">
                                <p class="event-date">{{ holiday.date }}</p>
                            </div>
                            <div class="event-content">
                                <p class="event-name">{{ holiday.name }}</p>
                                <p class="event-location">{{ holiday.location }}</p>
                            </div>
                        </li>
                    </ng-container>
                </ul>

                <p class="field-info preview-empty" *ngIf="!error && holidays.length === 0">
                    Select a country to see a preview.
                </p>
            </div>

            <app-copy-instructions-modal
                [visible]="showCopyModal"
                [instructions]="instructions"
                (closed)="showCopyModal = false"
            />
        </section>
    `,
})
export class HolidayPreviewComponent implements OnChanges {
    private readonly destroyRef = inject(DestroyRef);

    @Input() groupedHolidays: GroupedHolidaySection[] = [];
    @Input() holidays: HolidayItem[] = [];
    @Input() loading = false;
    @Input() error = "";
    @Input() icsUrl = "";

    readonly instructions = INSTRUCTION_CONFIGS;

    copyHint = "";
    showCopyModal = false;

    ngOnChanges(): void {
        if (!this.icsUrl) {
            this.copyHint = "";
        }
    }

    copyUrl(): void {
        if (!this.icsUrl) {
            return;
        }
        navigator.clipboard
            .writeText(this.icsUrl)
            .then(() => {
                this.copyHint = "";
                this.showCopyModal = true;
            })
            .catch(() => {
                this.showCopyModal = false;
                this.copyHint = "Copy failed. You can copy it manually.";
                timer(3000)
                    .pipe(takeUntilDestroyed(this.destroyRef))
                    .subscribe(() => {
                        this.copyHint = "";
                    });
            });
    }

    trackByGroup(_index: number, group: GroupedHolidaySection): string {
        return group.key;
    }

    trackByHoliday(_index: number, holiday: HolidayItem): string {
        return `${holiday.date}|${holiday.name}|${holiday.location}`;
    }
}
