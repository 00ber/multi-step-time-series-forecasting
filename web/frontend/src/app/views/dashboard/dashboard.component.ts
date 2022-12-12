import { Component, OnInit, ViewChild } from '@angular/core';
import { UntypedFormControl, UntypedFormGroup } from '@angular/forms';

import { DashboardChartsData, IChartProps } from './dashboard-charts-data';
import { Predictions, PredictionsService } from "../../predictions.service"
import * as moment from 'moment';
import { Subject } from 'rxjs';
import { ChartjsComponent } from '@coreui/angular-chartjs';

export interface TableRow {
  time: string;
  predicted: number;
  actual: number | null;
  error: number | null;
}

@Component({
  templateUrl: 'dashboard.component.html',
  styleUrls: ['dashboard.component.scss']
})
export class DashboardComponent implements OnInit {
  @ViewChild(ChartjsComponent, { static: true })
  predChart!: ChartjsComponent;

  constructor(private chartsData: DashboardChartsData, private predictionsApi: PredictionsService) {
  }

  public mainChart: IChartProps = {};
  public chart: Array<IChartProps> = [];

  public predicted: number[] = [];
  public actual: number[] = [];

  public tableRows$ = new Subject<TableRow[]>();
  
  public endDate: moment.Moment = moment(); 
  public startDate: moment.Moment =  moment(this.endDate).subtract(30, "days");
  public datesLabel: string = `${this.startDate.format("YYYY/MM/DD")} ~ ${this.endDate.format("YYYY/MM/DD")}`;
  public selectedDate!: string;


  ngOnInit(): void {
    this.initCharts();

    this.predictionsApi.$predictions.subscribe(data => {
      this.predicted = Object.keys(data).map(k => data[k].predicted)
      this.actual = Object.keys(data).map(k => data[k].actual).filter(i => !!i) as number[];
      const tableRows = this.toTableRows(data);
      this.tableRows$.next(tableRows)
      this.chartsData.initMainChart(tableRows);
    })
  }

  private getLabelText(label: string): string {
    const hour = label.slice(0,2)
    let hourValue = Number(hour);
    const suffix = (hourValue >= 12) ? "pm" : "am";
    if (hourValue > 12) {
      hourValue = hourValue - 12;
    }
    let labelTxt = `${hourValue} ${suffix}`;
    if (labelTxt == "0 am") {
      labelTxt = "12 am";
    }
    return labelTxt
  }

  private toTableRows(predictions: Predictions): TableRow[] {
    return Object.keys(predictions).map(datetime => {
      const time = datetime.slice(-8)
      const timeLabel = this.getLabelText(time);
      let error = null;
      const actual = predictions[datetime].actual;
      const predicted = predictions[datetime].predicted;
      if (!!actual) {
        error = actual - predicted
      } 
      return {
        time: timeLabel,
        predicted,
        actual,
        error
      }

    });

  }

  initCharts(): void {
    this.mainChart = this.chartsData.mainChart;
  }

  changeSelectedDate(selectedDate: string): void {
    this.selectedDate = selectedDate;
    this.tableRows$.next([])
    if(this.predChart.chart){
      this.mainChart.data.datasets.forEach((ds: any) => {
        ds.data = [];
      })
      this.predChart.chart.update()
    }
    this.predictionsApi.getPredictions(selectedDate)
  }
}
