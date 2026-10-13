"""Подключение к PostgreSQL. Параметры можно задать переменными окружения."""
import os
from contextlib import contextmanager

import psycopg2
from psycopg2.extras import RealDictCursor

DB_CONFIG = {
    "dbname": os.getenv("SHOESTORE_DB", "shoe_store"),
    "user": os.getenv("SHOESTORE_USER", "postgres"),
    "password": os.getenv("SHOESTORE_PASSWORD", "123456"),
    "host": os.getenv("SHOESTORE_HOST", "localhost"),
    "port": int(os.getenv("SHOESTORE_PORT", "5432")),
}

@contextmanager
def get_connection():
    """Open a connection, commit on success, roll back on failure, always close."""
    conn = psycopg2.connect(**DB_CONFIG, cursor_factory=RealDictCursor)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()
