import json
import boto3
import base64
import os
import uuid
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

BUCKET_NAME = os.environ['BUCKET_NAME']
TABLE_NAME = os.environ['TABLE_NAME']
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        body = json.loads(event['body'])
        filename = body['filename']
        file_content = base64.b64decode(body['content'])

        # Sécurité : extensions interdites
        if filename.lower().endswith(('.exe', '.sh')):
            return {
                'statusCode': 403,
                'body': json.dumps("Fichier interdit pour raisons de sécurité.")
            }

        file_id = str(uuid.uuid4())

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_id,
            Body=file_content
        )

        table.put_item(Item={
            'file_id': file_id,
            'original_name': filename,
            'upload_date': datetime.utcnow().isoformat(),
            'status': 'SECURE_STORED'
        })

        return {
            'statusCode': 200,
            'body': json.dumps(f"Fichier sécurisé avec succès. ID: {file_id}")
        }

    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps("Erreur interne.")
        }
