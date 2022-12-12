
import datetime
from datetime import date, timedelta

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
API_KEY = "e1f10a1e78da46f5b10a1e78da96f525"
BASE_URL = "https://api.weather.com/v1/location/KDCA:9:US/observations/historical.json?apiKey={api_key}&units=e&startDate={start_date}&endDate={end_date}"

urls = []
target_date = date(2000, 1, 1)
today = datetime.date.today()
while target_date != today:
    end_date = target_date + timedelta(days=1) 
    start_date_str = target_date.strftime("%Y%m%d")
    target_url = BASE_URL.format(api_key=API_KEY, start_date=start_date_str, end_date=start_date_str)
    urls.append(target_url)
    target_date = end_date

from concurrent.futures import ThreadPoolExecutor, as_completed
from time import perf_counter as time

from requests_cache import CachedSession


def send_requests():
    session = CachedSession('./data/weather_api_cache')
    start = time()

    with ThreadPoolExecutor(max_workers=16) as executor:
        future_to_url = {executor.submit(session.get, url): url for url in urls}

        for future in as_completed(future_to_url):
            url = future_to_url[future]
            response = future.result()
            from_cache = 'hit' if response.from_cache else 'miss'
            print(f'{url} is {len(response.content)} bytes (cache {from_cache})')

    print(f'Elapsed: {time() - start:.3f} seconds')


if __name__ == '__main__':
    send_requests()
    # send_requests()
