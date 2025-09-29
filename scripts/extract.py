import logging
import os
from time import sleep

import psycopg2
import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

API_URL = os.getenv('API_URL', 'https://jsonplaceholder.typicode.com/posts')
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def get_data_with_retry():
    for attempt in range(3):
        try:
            response = requests.get(API_URL, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            logger.warning(f"Attempt {attempt+1} failed: {str(e)}")
            sleep(2)
    raise Exception("Failed to fetch data after 3 attempts")

def save_to_db(data):
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    for item in data:
        cur.execute("""
            INSERT INTO raw_users_by_posts (user_id, post_id, title, body)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (post_id) DO NOTHING
        """, (item['userId'], item['id'], item['title'], item['body']))

    conn.commit()
    cur.close()
    conn.close()

if __name__ == '__main__':
    try:
        logger.info("Starting data extraction")
        data = get_data_with_retry()
        save_to_db(data)
        logger.info(f"Successfully processed {len(data)} records")
    except Exception as e:
        logger.error(f"Extraction failed: {str(e)}")
