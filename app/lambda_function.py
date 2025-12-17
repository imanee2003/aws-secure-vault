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
        # 1. Gestion flexible du body (Console vs API Gateway)
        if 'body' not in event:
             return {'statusCode': 400, 'body': 'Erreur: Body manquant'}
        
        body_content = event['body']
        if isinstance(body_content, str):
            body = json.loads(body_content)
        else:
            body = body_content

        filename = body.get('filename', 'inconnu.txt')
        content_encoded = body.get('content', '')

        # 2. Sécurité : Blocage des fichiers dangereux
        if filename.lower().endswith(('.exe', '.sh', '.bat')):
            print(f"ALERTE SÉCURITÉ: Fichier {filename} bloqué")
            return {
                'statusCode': 403,
                'body': json.dumps("Upload interdit : Type de fichier dangereux.")
            }

        # 3. Traitement
        file_content = base64.b64decode(content_encoded)
        file_id = str(uuid.uuid4())

        # 4. Upload chiffré (KMS est forcé côté Bucket, mais on le précise)
        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=file_id,
            Body=file_content
        )

        # 5. Métadonnées
        table.put_item(Item={
            'file_id': file_id,
            'original_name': filename,
            'upload_date': datetime.utcnow().isoformat(),
            'status': 'SECURE_STORED'
        })

        return {
            'statusCode': 200,
            'body': json.dumps(f"Succès : {filename} sécurisé (ID: {file_id})")
        }

    except Exception as e:
        print(f"ERREUR: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps("Erreur interne du serveur.")
        }