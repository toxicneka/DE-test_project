import logging
import os

import psycopg2

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'db'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'postgres'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'postgres')
}

def run_transform():
    conn = psycopg2.connect(**DB_CONFIG)
    cur = conn.cursor()

    # Очищаем таблицу перед вставкой новых данных (идемпотентность)
    cur.execute("TRUNCATE TABLE top_users_by_posts")

    # Вставляем обновленные данные
    cur.execute("""
        INSERT INTO top_users_by_posts (user_id, posts_cnt, calculated_at)
        SELECT
            user_id,
            COUNT(*) as posts_cnt,
            NOW() as calculated_at
        FROM raw_users_by_posts
        GROUP BY user_id
        ORDER BY posts_cnt DESC
    """)

    conn.commit()

    # Получаем количество обработанных записей
    cur.execute("SELECT COUNT(*) FROM top_users_by_posts")
    count = cur.fetchone()[0]

    cur.close()
    conn.close()
    logger.info(f"Transform completed successfully. Processed {count} records")

if __name__ == '__main__':
    try:
        logger.info("Starting transformation")
        run_transform()
    except Exception as e:
        logger.error(f"Transform failed: {str(e)}")
