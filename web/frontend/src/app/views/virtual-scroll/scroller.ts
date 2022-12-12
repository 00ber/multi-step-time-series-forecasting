import { CdkVirtualScrollViewport } from "@angular/cdk/scrolling";
import {
    ChangeDetectionStrategy,
    Component,
    EventEmitter,
    Input,
    Output,
    ViewChild,
    ViewEncapsulation
  } from "@angular/core";
  import * as moment from "moment";
  
  /** @title DatePicker by Horizontal virtual scroll */
  @Component({
    selector: "horizontal-date-scroller",
    styleUrls: ["scroller.css"],
    templateUrl: "scroller.html",
    encapsulation: ViewEncapsulation.None,
    changeDetection: ChangeDetectionStrategy.OnPush
  })
  
  export class HorizontalDateScroller {
    items: any[] = [];
    currentDate = new Date();
    currentMonth = "";
    stopDate = new Date();
    selectedItem = null;

    @Input() fromDate!: moment.Moment;
    @Input() toDate!: moment.Moment;

    @Output() dateChanged: EventEmitter<string> = new EventEmitter();
    
    @ViewChild(CdkVirtualScrollViewport) viewPort!: CdkVirtualScrollViewport;
 
    ngOnInit() {
      // Creating an array with specified date range

      this.items = this.getDates(this.fromDate, this.toDate);
      const [lastItem] = this.items.slice(-1)
      this.select(lastItem);
      setTimeout (() => {
        this.viewPort.scrollToIndex(this.items.indexOf(lastItem))
     }, 1000);
    }
  

    // Common method to create an array of dates
    getDates(fromDate: moment.Moment, toDate: moment.Moment) {
      let dateArray: string[] = [];
      // let endDate = moment();
      let currentDate = fromDate;
      while (currentDate <= toDate) {
        dateArray.push(currentDate.format("YYYY-MM-DD"));
        currentDate = moment(currentDate).add(1, "days");
      }
      return dateArray;
    }
  
    // Get the selected Date
    select(item: any) {
      this.selectedItem = item;
      this.dateChanged.emit(moment(this.selectedItem).format("YYYY-MM-DD"))
    }
  
    // Method for changing Month
    changeMonth(e: any) {
      const offset = this.viewPort.measureScrollOffset("end")    
      const renderedRange = this.viewPort.getRenderedRange();
      const renderedSize = this.viewPort.measureRangeSize(renderedRange)/(renderedRange.end - renderedRange.start)
      const totalSize = this.items.length * renderedSize;
      let indexNumer = Math.floor(((totalSize - offset)/totalSize) * this.items.length) - 1;
      this.currentDate = this.items[indexNumer];
      this.currentMonth = new Date(this.currentDate).toLocaleString("default", {month: "short"});
    }
  
    // Method to get the current weekday of the date showon
    returnWeekDay(item: any) {
      return moment(item, "YYYY-MM-DD").format("dddd").substring(0,3);
      // return new Date(item).toLocaleDateString("default", { weekday: "short" });
    }
  }
  