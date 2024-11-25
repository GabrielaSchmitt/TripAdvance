# environment variables: MONGODB_DATABASE - MONGODB_URI - S3_BUCKET

import json

def lambda_handler(event, context):
    # TODO implement
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }