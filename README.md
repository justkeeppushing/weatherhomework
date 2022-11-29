# Tiny Flask Weather API

This is a baby API that will suggest how to deal with the weather over one to five days. You supply it your location via lat,long, and it gives back a json response with information on the days requested.


## How to use (without docker):
Suggest using virtual python environments via `mkvirtualenv`, `virtualenvwrapper` in your developer setup, so there is no pip conflict with the system. 
```
mkvirtualenv weather
workon weather
pip3 install -r requirements.txt
flask run
```

API will be available at 127.0.0.1:5000/api .
You can set `FLASK_DEBUG` to 1 via `EXPORT FLASK_DEBUG=1` before launching `./app.py` for more verbose logging and stack tracing from Flask. By default, this is disabled.

If port 5000 is not available, you may change it via `export FLASK_RUN_PORT=5001` or to the port of your choosing for development.

When the application is running, Flask should display:
```
 🌈⤳ flask run
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```

### Call structure 
A typical call can be passed through your browser, or via curl, and looks like:
```
http://127.0.0.1:5000/api?num_days=5&orig_lat=47&orig_long=-122&start_date=22-11-2022
```

You can verify the call HTTP status from the `flask run` output.

Broken down, you will want to specify the following:

`num_days`: *from 1 to 5 days.*

`orig_lat`: *your latitude, in plain or decimal format.*

`orig_long`: *your longitude, in plain or decimal format.*

`start_date`: *the date to monitor, using DD-MM-YYYY format.*

This information is passed to *api.open-meteo.com* whose documentation and other functions (such as the source weather codes) can be found: https://open-meteo.com/en/docs


### How to use (with Docker):
Built using reference from this repo:
https://github.com/docker/awesome-compose/tree/master/nginx-wsgi-flask

Only thing changed was initial Docker base image, to alpine-python 3.6.9 to match my development environment.

`docker-compose up` from the /docker directory will start the nginx and flask processes, then be available at `http://127.0.0.1:8000/`  The API functionality is exactly the same as described above, just listens on a different port by default.
I merged their example /info and healthcheck endpoints into my app.py.

### Expected output example

```
{"47.01166, -122.04704": [{"2022-11-28": {"max": 34.7, "min": 29.2, "weather": "Slight snow showers", "Annotation:": "Brr, it's cold."}}, {"2022-11-29": {"max": 36.3, "min": 21.9, "weather": "Slight snow showers", "Annotation:": "Brr, it's cold."}}, {"2022-11-30": {"max": 36.7, "min": 26.9, "weather": "Slight snow showers", "Annotation:": "Brr, it's cold."}}, {"2022-12-01": {"max": 31.4, "min": 19.3, "weather": "Moderate snowfall", "Annotation:": "Brr, it's cold."}}, {"2022-12-02": {"max": 33.9, "min": 17.7, "weather": "Slight snowfall", "Annotation:": "Brr, it's cold."}}]}
```

You can use `jq` to parse it from command line, which prettifies and provide syntax hilighting for json objects.

```
 🌈⤳ curl -s "http://127.0.0.1:8000/api?num_days=5&orig_lat=47&orig_long=-122&start_date=28-11-2022" | jq
{
  "47.01166, -122.04704": [
    {
      "2022-11-28": {
        "max": 34.7,
        "min": 29.2,
        "weather": "Slight snow showers",
        "Annotation:": "Brr, it's cold."
      }
    },
    {
      "2022-11-29": {
        "max": 36.3,
        "min": 21.9,
        "weather": "Slight snow showers",
        "Annotation:": "Brr, it's cold."
      }
    },
    {
      "2022-11-30": {
        "max": 36.7,
        "min": 26.9,
        "weather": "Slight snow showers",
        "Annotation:": "Brr, it's cold."
      }
    },
    {
      "2022-12-01": {
        "max": 31.4,
        "min": 19.3,
        "weather": "Moderate snowfall",
        "Annotation:": "Brr, it's cold."
      }
    },
    {
      "2022-12-02": {
        "max": 33.9,
        "min": 17.7,
        "weather": "Slight snowfall",
        "Annotation:": "Brr, it's cold."
      }
    }
  ]
}
```

### Missing/Todo
Ideally, app.py would be split into two files, one with the healthchecks and one for the core application. and, the app.py source would be the same between /docker and /devel subdirectories, but I didn't want to spend too much time on it since this is only an example for the time being.


Currently, there is no exception trapping, but it would be nice to have Flask throw a polite error if the incorrect amount of API parameters are given. For the small project I feel Flask is pretty intuitive. In practice I would monitor for non-200 responses from the origin API and reprint whatever information it has to provide, for instance.


Nginx logging seems to be ommitting Flask /api GET data. 


No front end form, decided to skip that in favor of containerizing.
