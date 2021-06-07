import pandas as pd
import sys
import requests
import io
import boto3
import datetime
import json
import os


def call_API(path, params={}):
    res = requests.get("https://api.hennepin.us/api/jailroster/bookings/" + path,
                       params=params,
                       headers={
                           "Ocp-Apim-Subscription-Key": "6c62b8665d1048dc93ca46400dbca667"
                       })

    if res.status_code != 200:
        print("GET request failed " + path, file=sys.stderr)
        print(res, file=sys.stderr)
    else:
        return res


# startDate YYYY-MM-DD
# endDate   YYYY-MM-DD
# resStatus (type of record)
#            possible values
#            "": Show all (default)
#            "REL": Released from Custody
#            "IN":  In Custody
def get_all_bookings(startDate, endDate, resStatus=""):
    res = call_API("by-custody",
                  params={
                      "resStatus": resStatus,
                      "startDate": startDate,
                      "endDate": endDate
                  })

    if res.status_code == 200:
        return res.json()


def get_booking(bookingNumber):
    res = call_API(bookingNumber)

    try:
        return res.json()
    except ValueError:
        # Missing record
        print("JSONDecodeError for bookingNumber: " +
              bookingNumber, file=sys.stderr)


def convert_to_df(bookings_array):
    '''Write the bookings_array to a dataframe'''
    df = None
    for entry in bookings_array:
        row = pd.DataFrame.from_dict(entry)
        if df is None:
            df = row
        else:
            df = df.append(row, ignore_index=True)
    df = pd.concat([df.drop(['cases'], axis=1),
                    df['cases'].apply(pd.Series)], axis=1)
    df["receivedDayOfWeek"] = pd.to_datetime(df["receivedDateTime"], errors='ignore').dt.weekday_name
    for col in df.columns:
        if 'DateTime' in col:
          df[col] = pd.to_datetime(df[col], errors='ignore').dt.strftime("%Y-%m-%d %H:%M")
    return df


def write_csv(start_date, end_date, filename):
    '''Write the csv with booking info to a file'''
    bookings = get_all_bookings(start_date, end_date)
    finalOutput = []
    for booking in bookings:
        bookRes = get_booking(booking["bookingNumber"])
        if bookRes != None:
            finalOutput.append(bookRes)
    df = convert_to_df(finalOutput)

    bucket = os.environ['aws_bucket_name']
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False)
    s3_resource = boto3.resource(
        service_name='s3',
        region_name=os.environ['aws_region_name'],
        aws_access_key_id=os.environ['aws_access_key_id'],
        aws_secret_access_key=os.environ['aws_secret_access_key'])
    s3_resource.Object(bucket, filename).put(Body=csv_buffer.getvalue())
    return True


def lambda_handler(event, context):
    start_date = event['start_date']
    end_date = event['end_date']
    filename = event['filename']
    write_csv(start_date, end_date, filename)
    return True
