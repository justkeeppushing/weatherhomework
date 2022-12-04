#!/usr/bin/env python3
import flask
import json
import requests 
from dateutil import parser
import datetime
import time
import urllib
from flask import Flask, request, jsonify, abort
import logging

logging.basicConfig(format='%(asctime)s %(levelname)s in %(module)s: %(message)s', level=logging.DEBUG)
app = Flask(__name__)

# WMO Weather interpretation codes (WW)
weathercodes = { 0: 'Clear sky', 1: 'Mainly clear', 2: 'Partly cloudy', 3: 'Overcast', 45: 'Fog', 48: 'Depositing rime fog', 51: 'Light drizzle', 53: 'Moderate drizzle', 55: 'Dense drizzle', 56: 'Light freezing drizzle', 57: 'Dense freezing drizzle', 61: 'Slight rain', 63: 'Moderate rain', 65: 'Heavy rain', 66: 'Light freezing rain', 67: 'Heavy freezing rain', 71: 'Slight snowfall', 73: 'Moderate snowfall', 75: 'Heavy snowfall', 77: 'Snow grains', 80: 'Slight rain showers', 81: 'Moderate rain showers', 82: 'Violent rain showers', 85: 'Slight snow showers', 86: 'Heavy snow showers', 95: 'Slight or moderate thunderstorm', 96: 'Thunderstorm w/ slight hail', 99: 'Thunderstorm w/ heavy hail'} 

#@app.route('/')
#populate an index.html
#with a form that POSTs 

@app.route('/api')
def api():
  """
  Main component of project.
  Takes specified params and
  passes them off to a meteo api request,
  which is then fed into the next function
  that modifies the output before returning
  the results to Flask as json dump.
  """
# How to display which one is missing? List comparison to request.args()
# Then passing the param(s) missing to logger?
# Will give that a shot
  try:
    request.args.get("num_days")
    request.args.get("orig_lat")
    request.args.get("orig_long")
    request.args.get("start_date")
  except:
    app.logger.exception('Required paramater missing. Please see README.')
    abort(400)
  else:
    incoming_payload = request.args.to_dict()


  try:
    num_days = int(incoming_payload['num_days'])
  except:
    app.logger.exception('num_days must be an integer between 1 and 5.')
    abort(400)
  else:
    if not num_days in range(1,6):
      app.logger.exception('num_days must be between 1 and 5.')
      abort(400)
  num_days += -1

 
  try:
    orig_lat = float(incoming_payload['orig_lat']) 
    orig_long = float(incoming_payload['orig_long'])
  except:
    abort(400)
  else:
    if not orig_lat in range(-90,90):
      app.logger.exception('Latitude must be within normal ranges of -90 to 90.')
      abort(400)
    elif not orig_long in range(-180,180):
      app.logger.exception('Longitude must be within normal ranges of -180 to 180.')
      abort(400)

  try:
    start_date = parser.parse(incoming_payload['start_date']) #turn into datetime object
  except:
    app.logger.exception('start_date must be provided in MM-DD-YYYY format.')
    abort(400)
  else:
    if type(start_date) is datetime.datetime:
      end_date = start_date + datetime.timedelta(days=num_days) #so that addition works
    else: # superfluous ?
      app.logger.exception('start_date must be provided in MM-DD-YYYY format.')
      abort(400)


  meteo_api_params = urllib.parse.urlencode({
  'latitude': orig_lat,
  'longitude': orig_long,
  'daily': 'weathercode,temperature_2m_max,temperature_2m_min',
  'temperature_unit': 'fahrenheit',
  'timezone': 'auto',
  'start_date': start_date.strftime('%Y-%m-%d'),
  'end_date': end_date.strftime('%Y-%m-%d')
  }, safe=',') #this meteo api server didn't like encoded commas
  #using 'safe' kwarg from urlencode keeps it literal
  #otherwise it threw 400s

  url = 'https://api.open-meteo.com/v1/forecast?%s' % meteo_api_params


  try:
    with urllib.request.urlopen(url, timeout=10) as api_response:
      json_response = json.loads(api_response.read().decode('utf-8'))
      return(reformat_response(json_response))
  except urllib.request.HTTPError as e:
    app.logger.exception(e.code, e.reason)
  except urllib.request.URLError as e:
    app.logger.exception(e.reason)
   

def reformat_response(origin_response):
  """
  Iterating on the nested list/dicts
  and reformatting according to project.
  Weather results are replaced with
  the manual DB at the top,
  and logic applied to the min/max temps
  so we know what annotation to apply
  before returning it to /api.
  """
  resp_lat = origin_response['latitude']
  resp_long = origin_response['longitude']
  max_iter = origin_response['daily']['temperature_2m_max']
  min_iter = origin_response['daily']['temperature_2m_min']
  wc_iter = origin_response['daily']['weathercode']

  location = ', '.join(
    map(str, (resp_lat,resp_long)
    )
  )

  # use enumerate to access each item by index number
  # so i can update more than one value at once on the same iteration
  formatted_response = {
    location: [{
      date: {
        'max': max_iter[index],
        'min': min_iter[index],
        'weather': wc_iter[index]
        }
      } for index,date in enumerate(origin_response['daily']['time'])
    ]
  }

  # then swap out weather code from dict above
  for item in formatted_response.values():
      for nested in item:
          for wc in nested.values():
              if wc['weather'] in weathercodes.keys():
                  wc['weather'] = (weathercodes[wc['weather']])


  # and add annotation line by adding new key+value
  for item in formatted_response.values():
      for nested in item:
          for temp in nested.values():
              if temp['min'] < 30:
                  temp['Annotation:'] = "Brr, it's cold."
                  break
              elif temp['min'] < 50:
                  temp['Annotation:'] = "Better get a jacket."
                  break
              elif temp['max'] > 60:
                  temp['Annotation:'] = "What a nice day."
                  break
              elif temp['max'] > 80:
                  temp['Annotation:'] = "Wow, it's hot."
                  break
              else:
                  temp['Annotation:'] = "It's just a regular day."


  
  final_response = json.dumps(formatted_response)
  return final_response

if __name__ == "__main__":
    app.run()
