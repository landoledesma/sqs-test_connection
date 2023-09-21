import boto3
import hashlib
import json
from psycopg2.pool import SimpleConnectionPool
from datetime import datetime
import os
from dotenv import load_dotenv
import logging
import time

# Logging configuration
logging.basicConfig(level=logging.INFO)

# Load environment variables
load_dotenv()

# Connection Pool Configuration
DB_POOL = SimpleConnectionPool(
    minconn=1,
    maxconn=10,
    dbname=os.getenv('DB_NAME'), 
    user=os.getenv('DB_USER'), 
    password=os.getenv('DB_PASSWORD'), 
    host=os.getenv('DB_HOST'), 
    port=os.getenv('DB_PORT')
)

# Function to create hash
def create_hash(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()

# Function to process messages
def process_messages(messages, cursor):
    unmask_mapping = {}

    for message in messages:
        body = message['Body']
        message_id = message['MessageId']
        data = json.loads(body)
        device_id = data.get('device_id')
        ip = data.get('ip')

        cursor.execute("SELECT 1 FROM user_logins WHERE message_id = %s", (message_id,))
        if cursor.fetchone():
            logging.warning(f"Duplicated message has been skipped: {message_id}")
            continue

        if device_id and ip:
            unmask_mapping[create_hash(data['device_id'])] = data['device_id']
            unmask_mapping[create_hash(data['ip'])] = data['ip']
            
            data['device_id'] = create_hash(data['device_id'])
            data['ip'] = create_hash(data['ip'])
            
            cursor.execute("""
                INSERT INTO user_logins (user_id, device_type, masked_ip, masked_device_id, locale, app_version, create_date, message_id) 
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, (data['user_id'], data['device_type'], data['ip'], data['device_id'], data['locale'], data['app_version'], datetime.now().date(), message_id))
        else:
            logging.warning(f"Message with incomplete data: {data}")

    return unmask_mapping

def main():
    while True:  # Infinite loop
        try:
            sqs = boto3.client('sqs', endpoint_url='http://localhost:4566', region_name='us-east-1')
            response = sqs.receive_message(QueueUrl='http://localhost:4566/000000000000/login-queue', MaxNumberOfMessages=100)
            
            conn = DB_POOL.getconn()
            cursor = conn.cursor()
            
            messages = response.get('Messages', [])
            unmask_mapping = process_messages(messages, cursor)

            for hash_val, original_val in unmask_mapping.items():
                cursor.execute("""
                    INSERT INTO map_desmask (hash_val, original_val) 
                    VALUES (%s, %s)
                """, (hash_val, original_val))

            conn.commit()
        except Exception as e:
            logging.error(f"An error occurred: {e}")
        finally:
            cursor.close()
            DB_POOL.putconn(conn)

        time.sleep(1)  # Wait before checking again

if __name__ == "__main__":
    main()
