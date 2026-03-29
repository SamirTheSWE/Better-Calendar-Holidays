import { Component } from "@angular/core";

import { ErrorPageComponent } from "./error-page.component";

@Component({
    selector: "app-not-found",
    standalone: true,
    imports: [ErrorPageComponent],
    template: `
        <app-error-page
            code="404"
            title="Page Not Found"
            message="This page doesn't exist."
            [showHomeLink]="true"
        />
    `,
})
export class NotFoundComponent {}
