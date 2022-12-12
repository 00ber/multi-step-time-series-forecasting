from flask import Flask, request
import tensorflow as tf
from datetime import datetime, timedelta
import logging 
import requests
import requests_cache
import pandas as pd
import json
import numpy as np
import pickle
import math
import pytz

from flask_cors import CORS, cross_origin


session = requests_cache.CachedSession('requests-cache')

app = Flask(__name__)
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'

app.logger.setLevel(logging.INFO)
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
API_KEY = "e1f10a1e78da46f5b10a1e78da96f525"
BASE_URL = "https://api.weather.com/v1/location/KDCA:9:US/observations/historical.json?apiKey={api_key}&units=e&startDate={start_date}&endDate={end_date}"
model = tf.keras.models.load_model('/app/model', compile=False)

scaler = pickle.load(open('./model/scaler.pkl','rb'))
cols_to_scale = ["pressure", "wspd","heat_index","dewPt", "rh",	"vis", "wc", "wdir_degree", "clds_ordinal",
             "day_sin", "day_cos", "year_sin", "year_cos", "wdir_sin", "wdir_cos"]

def get_NaN_counts(df):    
    nan_counts = df.isna().sum()
    return pd.concat([nan_counts, ((nan_counts/len(df))*100).round(2)], 
                     axis=1, 
                     keys=["NaN count", "Percentage"])

def clds_to_ordinal(row):
  mapping = {
      "SKC": 0,
      "CLR": 0,
      "FEW": 1,
      "SCT": 2,
      "BKN": 3,
      "OVC": 4,
      "VV": 5
  }
  clds = row["clds"]
  if pd.isnull(clds):
      return np.NaN 
  return mapping[clds]

def clean_wspd(row):
  if row["wdir_cardinal"] == "CALM":
    return 0
  return row["wspd"]

def restrict_wspd(row):
  if row["wspd"] < 0:
    return 0
  return row["wspd"]

def restrict_rh(row):
  if row["rh"] < 0:
    return 0
  if row["rh"] > 100:
    return 100
  return row["rh"]

def clean_wdir(row):
  if row["wdir_cardinal"] == "CALM":
    return 0
  return row["wdir"]

def wdir_cardinal_to_deg(row):
    wdir = row["wdir"]
    if not pd.isnull(wdir):
      return wdir 
    cardinal_directions = {
        'N': 0,
        'NNE': 22.5,
        'NE': 45,
        'ENE': 67.5,
        'E': 90,
        'ESE': 112.5,
        'SE': 135,
        'SSE': 157.5,
        'S': 180,
        'SSW': 202.5,
        'SW': 225,
        'WSW': 247.5,
        'W': 270,
        'WNW': 292.5,
        'NW': 315,
        'NNW': 337.5,
        'CALM': 0,
        'VAR': -1
    }
    wdir_cardinal = row["wdir_cardinal"]
   
    return cardinal_directions[wdir_cardinal] if wdir_cardinal in cardinal_directions else np.NaN

def prepare_dataframe(_df, start_timestamp, end_timestamp):
  dates_df = pd.DataFrame()
  dates_df["obs_timestamp"] = pd.date_range(start_timestamp, end_timestamp, freq="H")

  _df = dates_df.merge(_df, how='left', on='obs_timestamp')
  _df = _df.astype(
      {
          'temp': 'float',
          'pressure': 'float',
          'wspd': 'float',
          'heat_index': 'float'
      },
  )

  _df["wdir_cardinal"].fillna(method="bfill", inplace=True)
  _df["wdir_degree"] = _df.apply(wdir_cardinal_to_deg, axis=1)
  _df["clds_ordinal"] = _df.apply(clds_to_ordinal, axis=1)
  _df["temp"].interpolate("polynomial", order=2, inplace=True)
  _df["pressure"].interpolate("polynomial", order=2, inplace=True)
  _df["heat_index"].interpolate("polynomial", order=2, inplace=True)
  _df["wdir"].fillna(method="bfill", inplace=True)
  _df["wdir"] = _df.apply(clean_wdir, axis=1)
  _df["wspd"] = _df.apply(clean_wspd, axis=1)
  _df["wspd"].interpolate("polynomial", order=2, inplace=True)
  _df["wspd"] = _df.apply(restrict_wspd, axis=1)
  _df["clds"].fillna(method="bfill", inplace=True)
  _df["clds_ordinal"].interpolate("linear", inplace=True)
  _df["dewPt"].interpolate("polynomial", order=2, inplace=True)
  _df["rh"].interpolate("polynomial", order=2, inplace=True)
  _df["rh"] = _df.apply(restrict_rh, axis=1)
  _df["wc"].interpolate("polynomial", order=2, inplace=True)
  _df["vis"].fillna(method="bfill", inplace=True)
  _df.drop(["wdir", "wdir_cardinal", "clds"], axis=1, inplace=True)

  _df = _df.dropna()

  _df = _df.sort_values(by=['obs_timestamp'])
  date_time = _df.pop('obs_timestamp')
  timestamp_s = date_time.map(pd.Timestamp.timestamp)
  day = 24*60*60
  year = (365.2425)*day
  
  _df['day_sin'] = np.sin(timestamp_s * (2 * np.pi / day))
  _df['day_cos'] = np.cos(timestamp_s * (2 * np.pi / day))
  _df['year_sin'] = np.sin(timestamp_s * (2 * np.pi / year))
  _df['year_cos'] = np.cos(timestamp_s * (2 * np.pi / year))
  _df['wdir_sin'] = np.sin(_df["wdir_degree"])
  _df['wdir_cos'] = np.cos(_df["wdir_degree"])

  return _df, date_time


def map_data_to_dataframe(data, target_date):
    end_timestamp = target_date - timedelta(minutes=8)
    start_timestamp = end_timestamp - timedelta(days=8) + timedelta(hours=1)
    
    df = pd.read_json(json.dumps(data))
    df["obs_timestamp"] = df.apply(lambda x: datetime.fromtimestamp(x["valid_time_gmt"]).strftime(DATE_FORMAT), axis=1)
    df = df.astype({'obs_timestamp': 'datetime64[ns]'})
    initial_cols = ["temp", "obs_timestamp", "pressure", "wspd", "heat_index", "dewPt", "rh", "vis", "wc", "wdir", "wdir_cardinal", "clds" ]
    df = df[initial_cols]
    
    df, _ = prepare_dataframe(df, start_timestamp.strftime(DATE_FORMAT), end_timestamp.strftime(DATE_FORMAT))
    return df 


def map_to_timestamp(predictions, target_date):
  start = target_date + timedelta(hours=1)
  end = start + timedelta(hours=23)
  target_hours = [x.to_pydatetime().strftime(DATE_FORMAT) for x in pd.date_range(start, end, freq="H")]
  return { h: predictions[idx] for idx, h in enumerate(target_hours)}

def predict(df):
    predict_df = df[-168:]
    predict_df_features = predict_df[cols_to_scale]
    predict_df_features = scaler.transform(predict_df_features.values)
    predict_df[cols_to_scale] = predict_df_features
    predictions = model(predict_df.to_numpy().reshape(1, 168, 16))
    return predictions

def predict_for_date(target_date):
    date_format = "%Y%m%d"
    start_date = target_date - timedelta(days=9)
    res = session.get(BASE_URL.format(api_key=API_KEY, start_date=start_date.strftime(date_format), end_date=target_date.strftime(date_format)))
    data = res.json()
    df = map_data_to_dataframe(data["observations"], target_date)
    predictions = predict(df)
    flattened = list(map(lambda x: math.floor(x), predictions.numpy().flatten().tolist()))
    return map_to_timestamp(flattened, target_date)

def get_actual_temperatures(target_date):
  date_format = "%Y%m%d"
  start_date = target_date - timedelta(days=1)  #Because api uses utc
  end_date = target_date + timedelta(days=1)
  start_date_str = (start_date - timedelta(days=1)).strftime(date_format)
  end_date_str = end_date.strftime(date_format)
  today = datetime.today().astimezone(pytz.timezone("America/New_York")).date()
  req_url = BASE_URL.format(api_key=API_KEY, start_date=start_date_str, end_date=end_date_str)
  if target_date.date() < today:
    res = session.get(req_url)
  else:
    res = requests.get(req_url)
  start_timestamp = target_date + timedelta(minutes=52)
  end_timestamp = end_date + timedelta(days=1) - timedelta(minutes=8)
  

  data = res.json()
  df = pd.read_json(json.dumps(data["observations"]))
  df["obs_timestamp"] = df.apply(lambda x: datetime.fromtimestamp(x["valid_time_gmt"]).astimezone(pytz.timezone("America/New_York")).strftime(DATE_FORMAT), axis=1)
  df = df.astype({'obs_timestamp': 'datetime64[ns]'})
  initial_cols = ["temp", "obs_timestamp"]
  df = df[initial_cols]
  dates_df = pd.DataFrame()
  dates_df["obs_timestamp"] = pd.date_range(start_timestamp, end_timestamp, freq="H")
  df = dates_df.merge(df, how='left', on='obs_timestamp')
 
  df["obs_timestamp"] = df.apply(lambda x: (x["obs_timestamp"] + timedelta(minutes=8)).strftime(DATE_FORMAT), axis=1)
  dicts =  df.to_dict("records")
  reduced = { k["obs_timestamp"]: k["temp"] for k in dicts}
  for k in reduced:
    if np.isnan(reduced[k]): 
      reduced[k] = None
  return reduced

@app.route("/predictions")
@cross_origin()
def get_predictions():
    today = datetime.today().astimezone(pytz.timezone("America/New_York")).date()
    target_date = datetime.strptime(request.args["target_date"], "%Y-%m-%d")
    app.logger.info(today)
    app.logger.info(target_date)
    # target_dates = list(filter(lambda x: x < today, [x.to_pydatetime() for x in pd.date_range(start_date, end_date, freq="D").to_list()]))
    predictions = predict_for_date(target_date)
    actual_temp = get_actual_temperatures(target_date) if target_date.date() <= today else None

    merged = { k: {"predicted": predictions[k], "actual": actual_temp[k] if actual_temp else None} for k in predictions}
    response = app.response_class(response=json.dumps(merged),
                                  status=200,
                                  mimetype='application/json')
    return response

