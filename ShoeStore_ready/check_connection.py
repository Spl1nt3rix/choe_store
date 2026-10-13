"""Проверка подключения к PostgreSQL без запуска интерфейса."""
from db import get_connection

try:
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user, version()")
            row = cur.fetchone()
    print("Подключение успешно.")
    print(f"База: {row['current_database']}")
    print(f"Пользователь: {row['current_user']}")
    print(row['version'])
except Exception as exc:
    print("Не удалось подключиться к PostgreSQL.")
    print(f"Причина: {exc}")
    raise SystemExit(1)
