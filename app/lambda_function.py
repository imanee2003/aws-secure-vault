import json
import boto3
import base64
import os
import uuid
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Variables d'environnement
BUCKET_NAME = os.environ['BUCKET_NAME']
TABLE_NAME = os.environ['TABLE_NAME']
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # Lecture du corps JSON
        body = json.loads(event['body'])
        filename = body['filename']
        file_content = base64.b64decode(body['content'])

        # 🔐 Vérification de sécurité : fichiers interdits
        if filename.lower().endswith('.exe') or filename.lower().endswith('.sh'):
            print("SECURITY_ALERT: Tentative d’upload d’un fichier potentiellement malveillant !")
            return {
                'statusCode': 403,
                'body': json.dumps("Fichier interdit pour raisons de sécurité.")
            }

        # ID unique du fichier
        file_id = str(uuid.uuid4())

        # Upload S3
        s3.put_object(Bucket=BUCKET_NAME, Key=file_id, Body=file_content)

        # Enregistrement en base DynamoDB
        table.put_item(Item={
            'file_id': file_id,
            'original_name': filename,
            'upload_date': str(datetime.now()),
            'status': 'SECURE_STORED'
        })

        return {
            'statusCode': 200,
            'body': json.dumps(f"Fichier {filename} sécurisé avec succès ! ID: {file_id}")
        }

    except Exception as e:
        print(f"ERROR: {e}")   # <--- utile pour CloudWatch Alarms aussi
        return {
            'statusCode': 500,
            'body': json.dumps("Erreur lors du traitement.")
        }
