"""Авторизация пользователей; отделена от интерфейса и запросов каталога."""
from db import get_connection

def authenticate(login: str, password: str):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """SELECT u.user_id, u.login, u.password_hash, u.full_name, r.role_name
                   FROM users u JOIN roles r ON r.role_id = u.role_id
                   WHERE u.login = %s""",
                (login,),
            )
            row = cur.fetchone()
    if not row:
        return None, "Пользователь с таким логином не найден"
    try:
        import bcrypt
        valid = bcrypt.checkpw(password.encode("utf-8"), row["password_hash"].encode("utf-8"))
    except (ValueError, TypeError, AttributeError):
        valid = False
    if not valid:
        return None, "Неверный логин или пароль"
    row.pop("password_hash", None)
    return row, None
