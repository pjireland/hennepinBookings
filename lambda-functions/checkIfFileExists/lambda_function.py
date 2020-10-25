import json
import boto3
import os


def lambda_handler(event, context):
    filename = event['queryStringParameters']['filename']

    s3 = boto3.resource(
        service_name='s3',
        region_name=os.environ['aws_region_name'],
        aws_access_key_id=os.environ['aws_access_key_id'],
        aws_secret_access_key=os.environ['aws_secret_access_key'])

    try:
        data = s3.Object(os.environ['aws_bucket_name'], filename).get()
        contents = data['Body'].read().decode('utf-8')
    except:
        return {
            'statusCode': 200,
            'body': json.dumps({'filename': filename, 'success': 0})
        }
    else:
        # The object does exist.
        return {
            'statusCode': 200,
            'body': json.dumps(
                {
                    'filename': filename,
                    'success': 1,
                    'contents': contents
                })
        }
