import { Injectable } from '@angular/core';
import { getStyle, hexToRgba } from '@coreui/utils/src';
import { Predictions } from 'src/app/predictions.service';
import { TableRow } from './dashboard.component';

export interface IChartProps {
  data?: any;
  labels?: any;
  options?: any;
  colors?: any;
  type?: any;
  legend?: any;

  [propName: string]: any;
}

@Injectable({
  providedIn: 'any'
})
export class DashboardChartsData {
  public mainChart: IChartProps = {};
  public predicted: number[] = [];
  public actual: number[] = [];


  initMainChart(data: TableRow[]) {
    const styleActual = '#20a8d8';
    const stylePredicted = '#f86c6b';
    const stylePredictedBg = hexToRgba(getStyle('--cui-info'), 10) ?? '#20a8d8';

    this.predicted = data.map(d => d.predicted)
    this.actual = data.map(d => d.actual).filter(d => !!d) as number[];
    this.mainChart['elements'] = data.length;
    this.mainChart['Predicted'] = this.predicted;
    this.mainChart['Actual'] = this.actual;

    let labels: string[] = data.map(d => d.time);

    const colors = [
      {
        // stylePredicted
        backgroundColor: stylePredictedBg,
        borderColor: stylePredicted,
        borderDash: [5, 5],
        pointHoverBackgroundColor: stylePredicted,
        fill: "+1",
      },
      {
        // styleActual
        backgroundColor: 'transparent',
        borderColor: styleActual,
        pointHoverBackgroundColor: '#fff',
        fill: true
      },
    ];

    const datasets = [
      {
        data: this.mainChart['Predicted'],
        label: 'Predicted',
        ...colors[0]
      },
      {
        data: this.mainChart['Actual'],
        label: 'Actual',
        ...colors[1]
      }
    ];
    // if(this.mainChart["Actual"].length > 0) {
    //   datasets.push(
        
    //   )
    // }

    const plugins = {
      legend: {
        display: true,
        position: "top"
      },
      tooltip: {
        callbacks: {
          labelColor: function(context: any) {
            return {
              backgroundColor: context.dataset.borderColor
            };
          }
        }
      }
    };

    const options = {
      maintainAspectRatio: false,
      plugins,
      scales: {
        x: {
          grid: {
            drawOnChartArea: true
          }
        },
        y: {
          beginAtZero: true,
          max: 100,
          ticks: {
            callback: (val: string, _index: number, _ticks: unknown) => {
              return `${val} °F`
            },
            maxTicksLimit: 20,
            stepSize: 5
          }
        }
      },
      elements: {
        line: {
          tension: 0
        },
        point: {
          radius: 0,
          hitRadius: 10,
          hoverRadius: 4,
          hoverBorderWidth: 3
        }
      }
    };

    this.mainChart.type = 'line';
    this.mainChart.options = options;
    this.mainChart.data = {
      datasets,
      labels
    };
  }

}
