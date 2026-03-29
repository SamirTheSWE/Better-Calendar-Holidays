import { Component, EventEmitter, Input, Output } from "@angular/core";
import { RouterLink } from "@angular/router";

@Component({
    selector: "app-error-page",
    standalone: true,
    imports: [RouterLink],
    template: `
        <div class="error-page">
            <p class="error-code">{{ code }}</p>
            <h1 class="error-title">{{ title }}</h1>
            <p class="error-message">{{ message }}</p>
            @if (showRetry) {
                <button class="btn-primary" (click)="retryClicked.emit()">Try Again</button>
            }
            @if (showHomeLink) {
                <a routerLink="/" class="btn-primary">Return to Home</a>
            }
        </div>
    `,
})
export class ErrorPageComponent {
    @Input() code = "";
    @Input() title = "";
    @Input() message = "";
    @Input() showRetry = false;
    @Input() showHomeLink = false;
    @Output() retryClicked = new EventEmitter<void>();
}
