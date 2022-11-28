# Tiny Flask Weather API

### How to use (with Docker):

https://raw.githubusercontent.com/docker/awesome-compose/master/nginx-wsgi-flask/compose.yaml

### How to use (without docker):
Suggest using virtual python environments via `mkvirtualenv`, `virtualenvwrapper` in your developer setup, so there is no pip conflict with the system. 
```
mkvirtualenv weather
workon weather
pip3 install -f requirements.txt
flask run
```

API will be available at 127.0.0.1:5000/api .
You can set `FLASK_DEBUG` to 1 via `EXPORT FLASK_DEBUG=1` before launching `./app.py` for more verbose logging and stack tracing from Flask. By default, this is disabled.

If port 5000 is not available, you may change it via `export FLASK_RUN_PORT=5001` or to the port of your choosing before launch.

When the application is running, Flask should display:
```
 🌈⤳ flask run
 * Environment: production
   WARNING: This is a development server. Do not use it in a production deployment.
   Use a production WSGI server instead.
 * Debug mode: off
 * Running on http://127.0.0.1:5000/ (Press CTRL+C to quit)
```
 
A typical call can be passed through your browser, or via curl, and looks like:
```
http://127.0.0.1:5000/api?num_days=5&orig_lat=47&orig_long=-122&start_date=22-11-2022
```

You can verify the call HTTP status from the `flask run` output.

Broken down, you will want to specify the following:

`num_days`: from 1 to 5 days.
`orig_lat`: your latitude, in plain or decimal format.
`orig_long`: your longitude, in plain or decimal format.
`start_date`: the date to monitor, using DD-MM-YYYY format.

This information is passed to *api.open-meteo.com* whose documentation and other functions (such as the source weather codes) can be found: https://open-meteo.com/en/docs
