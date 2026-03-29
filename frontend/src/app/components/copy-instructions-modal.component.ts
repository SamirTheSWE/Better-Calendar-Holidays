import { CommonModule } from "@angular/common";
import { Component, EventEmitter, HostListener, Input, Output } from "@angular/core";

export interface InstructionConfig {
    id: string;
    label: string;
    steps: string[];
}

export const INSTRUCTION_CONFIGS: InstructionConfig[] = [
    {
        id: "outlook",
        label: "Microsoft Outlook",
        steps: [
            "Open Outlook Calendar and click Add calendar.",
            "Select Subscribe from web.",
            "Paste the copied ICS URL and confirm.",
        ],
    },
    {
        id: "apple",
        label: "Apple",
        steps: [
            "Open Calendar app and go to File.",
            "Choose New Calendar Subscription.",
            "Paste the copied ICS URL and subscribe.",
        ],
    },
    {
        id: "google",
        label: "Google",
        steps: [
            "Open Google Calendar settings.",
            "Choose Add calendar then From URL.",
            "Paste the copied ICS URL and add calendar.",
        ],
    },
];

@Component({
    selector: "app-copy-instructions-modal",
    standalone: true,
    imports: [CommonModule],
    template: `
        <div class="modal-backdrop" *ngIf="visible" (click)="closed.emit()">
            <div
                class="copy-modal"
                role="dialog"
                aria-modal="true"
                aria-labelledby="copy-modal-title"
                (click)="$event.stopPropagation()"
            >
                <button
                    type="button"
                    class="modal-close"
                    (click)="closed.emit()"
                    aria-label="Close"
                >
                    x
                </button>
                <div class="modal-header">
                    <p class="modal-kicker">URL Copied</p>
                    <h3 id="copy-modal-title" class="modal-title">Add it to your calendar</h3>
                    <p class="modal-summary">
                        Subscribe once to keep your holidays updated automatically.
                    </p>
                </div>
                <div class="modal-platform-row">
                    <p class="modal-platform-label">Platform:</p>
                    <div class="modal-tabs">
                        <button
                            *ngFor="let config of instructions"
                            type="button"
                            class="modal-tab"
                            [class.active]="activeTab === config.id"
                            (click)="activeTab = config.id"
                        >
                            {{ config.label }}
                        </button>
                    </div>
                </div>
                <section class="modal-instructions">
                    <ng-container *ngFor="let config of instructions">
                        <ol class="modal-steps" *ngIf="activeTab === config.id">
                            <li *ngFor="let step of config.steps">{{ step }}</li>
                        </ol>
                    </ng-container>
                </section>
                <button type="button" class="btn-secondary modal-action" (click)="closed.emit()">
                    Got It!
                </button>
            </div>
        </div>
    `,
})
export class CopyInstructionsModalComponent {
    @Input() visible = false;
    @Input() instructions: InstructionConfig[] = INSTRUCTION_CONFIGS;
    @Input() activeTab = "outlook";

    @Output() closed = new EventEmitter<void>();

    @HostListener("document:keydown.escape")
    onEscapePressed(): void {
        if (this.visible) {
            this.closed.emit();
        }
    }
}
