import { NgModule } from '@angular/core';
import { CommonModule } from '@angular/common';
import { ReactiveFormsModule } from '@angular/forms';
import {MatNativeDateModule} from '@angular/material/core';
import {
  CardModule,
  GridModule,
  NavModule
} from '@coreui/angular';
import { MatDatepickerModule } from '@angular/material/datepicker';

import { AboutComponent } from './about.component';
import { AboutRoutingModule } from './about-routing.module'

@NgModule({
  imports: [
    CardModule,
    AboutRoutingModule
  ],
  declarations: [AboutComponent],
})
export class AboutModule {
}
