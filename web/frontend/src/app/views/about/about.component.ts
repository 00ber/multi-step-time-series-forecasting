import { Component } from '@angular/core';


export interface TableRow {
  time: string;
  predicted: number;
  actual: number | null;
  error: number | null;
}

@Component({
    selector: 'about',
    templateUrl: 'about.component.html'
})
export class AboutComponent {}
