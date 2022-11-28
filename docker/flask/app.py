#!/usr/bin/env python3
import flask
import json
import requests 
from dateutil import parser
import datetime
import time
import urllib
from flask import Flask, request, jsonify 

app = Flask(__name__)

# WMO Weather interpretation codes (WW)
weathercodes = {
 0: 'Clear sky',
 1: 'Mainly clear',
 2: 'Partly cloudy',
 3: 'Overcast',
 45: 'Fog',
 48: 'Depositing rime fog',
 51: 'Light drizzle',
 53: 'Moderate drizzle',
 55: 'Dense drizzle',
 56: 'Light freezing drizzle',
 57: 'Dense freezing drizzle',
 61: 'Slight rain',
 63: 'Moderate rain',
 65: 'Heavy rain',
 66: 'Light freezing rain',
 67: 'Heavy freezing rain',
 71: 'Slight snowfall',
 73: 'Moderate snowfall',
 75: 'Heavy snowfall',
 77: 'Snow grains',
 80: 'Slight rain showers',
 81: 'Moderate rain showers',
 82: 'Violent rain showers',
 85: 'Slight snow showers',
 86: 'Heavy snow showers',
 95: 'Slight or moderate thunderstorm',
 96: 'Thunderstorm w/ slight hail',
 99: 'Thunderstorm w/ heavy hail'}

# https://github.com/docker/awesome-compose/tree/master/nginx-wsgi-flask
@app.route('/')
def hello():
        return "Hello World!"

@app.route('/cache-me')
def cache():
        return "nginx will cache this response"

@app.route('/info')
def info():

        resp = {
                'connecting_ip': request.headers['X-Real-IP'],
                'proxy_ip': request.headers['X-Forwarded-For'],
                'host': request.headers['Host'],
                'user-agent': request.headers['User-Agent']
        }

        return jsonify(resp)

@app.route('/flask-health-check')
def flask_health_check():
        return "success"
####

# my code 
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
  incoming_payload = request.args.to_dict()
  num_days = int(incoming_payload['num_days']) - 1 #because python starts at 0
  if num_days > 5:
    return("Please keep number of days at or under 5.")
  
  orig_lat = incoming_payload['orig_lat']
  orig_long = incoming_payload['orig_long']
  start_date = parser.parse(incoming_payload['start_date']) #turn into datetime object
  end_date = start_date + datetime.timedelta(days=num_days) #so that addition works


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

  print(url)

  with urllib.request.urlopen(url) as api_response:
    #print(api_response.read().decode('utf-8'))
    json_response = json.loads(api_response.read().decode('utf-8'))
    return(reformat_response(json_response))
 

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
  print(final_response)
  return final_response

if __name__ == "__main__":
    app.run()
