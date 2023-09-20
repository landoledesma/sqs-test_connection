import boto3
import hashlib
import json
import psycopg2
from psycopg2.pool import SimpleConnectionPool
from datetime import datetime
import os
from dotenv import load_dotenv
import logging

# Configuración de logging
logging.basicConfig(level=logging.INFO)

# Cargar variables de entorno
load_dotenv()

# Configuración de Connection Pool
DB_POOL = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname=os.getenv('DB_NAME'), 
    user=os.getenv('DB_USER'), 
    password=os.getenv('DB_PASSWORD'), 
    host=os.getenv('DB_HOST'), 
    port=os.getenv('DB_PORT')
)

# Función para crear hash
def crear_hash(cadena):
    return hashlib.sha256(cadena.encode('utf-8')).hexdigest()

# Función para procesar mensajes
def procesar_mensajes(mensajes, cursor):
    mapeo_desenmascaramiento = {}

    for mensaje in mensajes:
        cuerpo = mensaje['Body']
        datos = json.loads(cuerpo)
        device_id = datos.get('device_id')
        ip = datos.get('ip')

        if device_id and ip:
            mapeo_desenmascaramiento[crear_hash(datos['device_id'])] = datos['device_id']
            mapeo_desenmascaramiento[crear_hash(datos['ip'])] = datos['ip']
            
            datos['device_id'] = crear_hash(datos['device_id'])
            datos['ip'] = crear_hash(datos['ip'])
            
            cursor.execute("""
                INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date) 
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (datos['user_id'], datos['device_type'], datos['ip'], datos['device_id'], datos['locale'], datos['app_version'], datetime.now().date()))
        else:
            logging.warning(f"Mensaje con datos incompletos: {datos}")

    return mapeo_desenmascaramiento

# Función principal
def main():
    try:
        sqs = boto3.client('sqs', endpoint_url='http://localhost:4566', region_name='us-east-1')
        response = sqs.receive_message(QueueUrl='http://localhost:4566/000000000000/login-queue', MaxNumberOfMessages=100)
        
        conn = DB_POOL.getconn()
        cursor = conn.cursor()
        
        mensajes = response.get('Messages', [])
        mapeo_desenmascaramiento = procesar_mensajes(mensajes, cursor)

        for hash_val, original_val in mapeo_desenmascaramiento.items():
            cursor.execute("""
                INSERT INTO mapeo_desenmascaramiento (hash_val, original_val) 
                VALUES (%s, %s)
            """, (hash_val, original_val))

        conn.commit()
    except Exception as e:
        logging.error(f"Ocurrió un error: {e}")
    finally:
        cursor.close()
        DB_POOL.putconn(conn)

if __name__ == "__main__":
    main()
