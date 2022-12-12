import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { environment } from './../environments/environment';


export interface Predictions {
  [k: string]: {
    predicted: number;
    actual: number | null
  }
}

@Injectable({
  providedIn: 'root'
})
export class PredictionsService {

  public $predictions = new BehaviorSubject<Predictions>({})
  constructor(private http: HttpClient) { }

  public getPredictions(targetDate: string): void {
    this.http.get<Predictions>(`${environment.apiUrl}/predictions`, { params: { target_date: targetDate }}).subscribe(data => {
      this.$predictions.next(data)
    })
  }
}
