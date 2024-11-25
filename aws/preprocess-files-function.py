# environment variables: MONGODB_DATABASE - MONGODB_URI - S3_BUCKET

import logging
import json
import boto3
import pandas as pd
import pymongo
import os
import base64
import io
from bson import ObjectId
from datetime import datetime


# Configurar logging
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def preprocess_dataframe(df):
    """
    Função centralizada de pré-processamento específica para dados de voos
    """
    try:
        logger.info("Iniciando pré-processamento do DataFrame.")
        # Conversão e padronização de colunas
        logger.debug(f"Colunas antes do pré-processamento: {df.columns}")
        df['date'] = pd.to_datetime(df['date(DD/MM/YYYY)'], format='%Y-%m-%d', errors='coerce')
        df['duration'] = pd.to_numeric(df['duration(minutes)'], errors='coerce')
        df['price'] = pd.to_numeric(df['price(dol)'], errors='coerce')
        
        # Remover colunas originais após conversão
        df = df.drop(columns=['date(DD/MM/YYYY)', 'duration(minutes)', 'price(dol)'])
        logger.debug(f"Colunas após remoção: {df.columns}")
        
        # Validações e limpeza
        df.dropna(subset=['date', 'duration', 'price'], inplace=True)
        logger.info(f"Pré-processamento concluído. Linhas processadas: {len(df)}")
        
        # Feature engineering opcional
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.dayofweek
        
        return df
    except Exception as e:
        logger.error(f"Erro no pré-processamento: {e}")
        raise

def lambda_handler(event, context):
    logger.info("Lambda Function iniciada.")
    
    # Validar payload recebido do trigger do MongoDB
    if not event or 'arquivos' not in event:
        logger.error("Payload inválido ou ausente.")
        logger.debug(f"Payload recebido: {json.dumps(event, indent=2)}")
        return {
            'statusCode': 400,
            'body': json.dumps({'error': 'Payload inválido'})
        }
    
    # Inicializar clientes
    s3_client = boto3.client('s3')
    bucket_name = os.environ['S3_BUCKET']
    mongo_uri = os.environ['MONGODB_URI']
    database_name = os.environ.get('MONGODB_DATABASE', 'tripadv_qas')

    try:
        logger.info(f"Conectando ao MongoDB em {mongo_uri}.")
        mongo_client = pymongo.MongoClient(mongo_uri)
        db = mongo_client[database_name]
        logger.info("Conexão com MongoDB estabelecida.")

        processed_files = []
        total_processed_size = 0
        
        for arquivo in event['arquivos']:
            logger.info(f"Processando arquivo: {arquivo['id']}.")
            try:
                file_id = ObjectId(arquivo['id'])
                df = pd.DataFrame(arquivo['data'])
                logger.debug(f"DataFrame inicial: {df.head()}")

                preprocessed_df = preprocess_dataframe(df)
                logger.debug(f"DataFrame pré-processado: {preprocessed_df.head()}")

                s3_key = f"preprocessed/{arquivo['id']}_preprocessed.csv"
                csv_buffer = io.StringIO()
                preprocessed_df.to_csv(csv_buffer, index=False)
                
                s3_client.put_object(
                    Bucket=bucket_name,
                    Key=s3_key,
                    Body=csv_buffer.getvalue()
                )
                logger.info(f"Arquivo {arquivo['id']} salvo no S3: {s3_key}.")

                processed_files.append({
                    'id': str(file_id),
                    's3_path': s3_key,
                    'original_filename': arquivo.get('nome', 'unknown'),
                    'processed_rows': len(preprocessed_df)
                })

                total_processed_size += arquivo.get('size', 0)

            except Exception as file_error:
                logger.error(f"Erro processando arquivo {arquivo['id']}: {file_error}")
                continue
        
        mongo_client.close()
        logger.info("Conexão com MongoDB encerrada.")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'processed_files': processed_files,
                'total_processed': len(processed_files),
                'total_processed_size': total_processed_size
            })
        }
    
    except Exception as e:
        logger.error(f"Erro crítico na Lambda Function: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps({
                'error': str(e),
                'status': 'failed'
            })
        }