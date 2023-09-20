import boto3
import hashlib
import json
import psycopg2
from datetime import datetime
import os
from dotenv import load_dotenv
# Cargar las variables de entorno del archivo .env
load_dotenv()

# Establecer credenciales a partir de las variables de entorno
os.environ['AWS_ACCESS_KEY_ID'] = os.getenv('AWS_ACCESS_KEY_ID')
os.environ['AWS_SECRET_ACCESS_KEY'] = os.getenv('AWS_SECRET_ACCESS_KEY')
os.environ['AWS_SESSION_TOKEN'] = os.getenv('AWS_SESSION_TOKEN')

# Conexión a la base de datos PostgreSQL utilizando variables de entorno
conn = psycopg2.connect(dbname=os.getenv('DB_NAME'), user=os.getenv('DB_USER'), password=os.getenv('DB_PASSWORD'), host=os.getenv('DB_HOST'), port=os.getenv('DB_PORT'))
cursor = conn.cursor()

# Conectar con AWS SQS (en localstack)
sqs = boto3.client('sqs', endpoint_url='http://localhost:4566', region_name='us-east-1')

# Obtener los mensajes de la cola
response = sqs.receive_message(
    QueueUrl='http://localhost:4566/000000000000/login-queue',
    MaxNumberOfMessages=100,
)

# Diccionario para almacenar el mapeo original a hash
mapeo_desenmascaramiento = {}

# Función para crear un hash de una cadena
def crear_hash(cadena):
    return hashlib.sha256(cadena.encode('utf-8')).hexdigest()

# Procesar cada mensaje
for mensaje in response.get('Messages', []):
    # Obtener el cuerpo del mensaje y cargarlo como JSON
    cuerpo = mensaje['Body']
    datos = json.loads(cuerpo)
    # Obtener device_id y ip, devolverá None si las claves no existen
    device_id = datos.get('device_id')
    ip = datos.get('ip')
    if device_id and ip:
        # Guardar la información original en el diccionario de mapeo
        mapeo_desenmascaramiento[crear_hash(datos['device_id'])] = datos['device_id']
        mapeo_desenmascaramiento[crear_hash(datos['ip'])] = datos['ip']
        
        # Reemplazar los valores de device_id e ip con su versión hash
        datos['device_id'] = crear_hash(datos['device_id'])
        datos['ip'] = crear_hash(datos['ip'])
        
        # Insertar los datos procesados en la base de datos PostgreSQL
        cursor.execute("""
            INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date) 
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (datos['user_id'], datos['device_type'], datos['ip'], datos['device_id'], datos['locale'], datos['app_version'], datetime.now().date()))
    else:
        print(f"Mensaje con datos incompletos: {datos}")
# Guardar el diccionario de mapeo en la base de datos
for hash_val, original_val in mapeo_desenmascaramiento.items():
    cursor.execute("""
        INSERT INTO mapeo_desenmascaramiento (hash_val, original_val) 
        VALUES (%s, %s)
    """, (hash_val, original_val))

# Confirmar las transacciones
conn.commit()

# Cerrar la conexión
cursor.close()
conn.close()
