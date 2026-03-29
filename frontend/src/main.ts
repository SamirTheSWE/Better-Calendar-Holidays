import { provideHttpClient } from "@angular/common/http";
import { bootstrapApplication } from "@angular/platform-browser";
import { provideRouter } from "@angular/router";

import { AppComponent } from "./app/app.component";
import { HomeComponent } from "./app/home/home.component";
import { NotFoundComponent } from "./app/components/not-found.component";

void bootstrapApplication(AppComponent, {
    providers: [
        provideHttpClient(),
        provideRouter([
            { path: "", component: HomeComponent },
            { path: "**", component: NotFoundComponent },
        ]),
    ],
});
