from datetime import datetime as dt
import datetime
import dash
import dash_html_components as html
import dash_core_components as dcc
import requests
import io
import flask
import json
import time
import re

today = datetime.datetime.today()
tomorrow = today + datetime.timedelta(days=1)

# Initiate the app
app = dash.Dash(__name__)
application = app.server
app.title = 'Retrieve CSV of Hennepin County Bookings'

# Set up the layout
app.layout = html.Div(children=[
    html.H1(children='Hennepin County Bookings'),
    html.H2(children='Select date range for bookings:'),
    dcc.DatePickerRange(
        id='my-date-picker-range',
        min_date_allowed=datetime.datetime(2016, 1, 1),
        max_date_allowed=datetime.datetime(
            tomorrow.year, tomorrow.month, tomorrow.day),
        initial_visible_month=datetime.datetime(
            today.year, today.month, today.day),
        start_date=datetime.datetime(
            today.year, today.month, today.day).date(),
        end_date=datetime.datetime(
            tomorrow.year, tomorrow.month, tomorrow.day).date()
    ),
    html.Div(html.A('Download CSV', id='output-container-download'))
])


@app.callback(
    dash.dependencies.Output('output-container-download', 'href'),
    [dash.dependencies.Input('my-date-picker-range', 'start_date'),
     dash.dependencies.Input('my-date-picker-range', 'end_date')])
def update_output(start_date, end_date):
    if start_date is not None and end_date is not None:
        start_date = dt.strptime(re.split('T| ', start_date)[0], '%Y-%m-%d')
        start_date_string = start_date.strftime('%Y-%m-%d')
        end_date = dt.strptime(re.split('T| ', end_date)[0], '%Y-%m-%d')
        end_date_string = end_date.strftime('%Y-%m-%d')
        return '/dash/urlToDownload?start_date={}'.format(start_date_string) + '&end_date={}'.format(end_date_string)
    else:
        return ''


@app.server.route('/dash/checkIfReady')
def check_if_ready():
    filename = flask.request.args.get('filename')
    res = requests.get(
        'https://1d7flaad72.execute-api.us-east-1.amazonaws.com/default/checkIfFileExists',
        params={'filename': filename}
    )
    if res.json()['success']:
        mem = io.BytesIO()
        mem.write(res.json()['contents'].encode('utf-8'))
        mem.seek(0)
        return flask.send_file(mem,
                               mimetype='text/csv',
                               attachment_filename='bookings.csv',
                               as_attachment=True,
                               cache_timeout=0)
    else:
        time.sleep(50)
        return flask.redirect('/dash/checkIfReady?filename=' + filename)


@app.server.route('/dash/urlToDownload')
def get_csv():
    start_date = flask.request.args.get('start_date')
    end_date = flask.request.args.get('end_date')

    res = requests.get(
        'https://hhxevjmh98.execute-api.us-east-1.amazonaws.com/default/hennepin-test',
        params={'start_date': start_date, 'end_date': end_date}
    )
    if res.status_code == 200:
        resJson = res.json()
        print(resJson)
        filename = resJson['filename']
        filepath = 'https://hennepin-bookings-data.s3.amazonaws.com/' + filename
        return flask.redirect('/dash/checkIfReady?filename=' + filename)
    else:
        return 'Error'


# Run the app
if __name__ == '__main__':
    application.run(debug=True, port=8080)
