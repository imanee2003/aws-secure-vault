import json
import boto3
import base64
import os
import uuid
from datetime import datetime

s3 = boto3.client('s3')
dynamodb = boto3.resource('dynamodb')

# Récupération des noms depuis les variables d'environnement
BUCKET_NAME = os.environ['BUCKET_NAME']
TABLE_NAME = os.environ['TABLE_NAME']
table = dynamodb.Table(TABLE_NAME)

def lambda_handler(event, context):
    try:
        # 1. Simuler la réception d'un fichier (en JSON pour simplifier l'API)
        # On attend un body : { "filename": "test.txt", "content": "base64encoded..." }
        body = json.loads(event['body'])
        filename = body['filename']
        file_content = base64.b64decode(body['content'])
        file_id = str(uuid.uuid4())
        
        # 2. Upload vers S3 (Stockage Cloud)
        s3.put_object(Bucket=BUCKET_NAME, Key=file_id, Body=file_content)
        
        # 3. Écriture des métadonnées (Base de données Cloud)
        table.put_item(Item={
            'file_id': file_id,
            'original_name': filename,
            'upload_date': str(datetime.now()),
            'status': 'SECURE_STORED'
        })
        
        return {
            'statusCode': 200,
            'body': json.dumps(f"Fichier {filename} sécurisé avec succès! ID: {file_id}")
        }
        
    except Exception as e:
        print(e)
        return {
            'statusCode': 500,
            'body': json.dumps("Erreur lors du traitement.")
        }