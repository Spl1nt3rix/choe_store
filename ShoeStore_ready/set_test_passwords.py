# Set one known test password for all demo accounts. Run after init_db.sql.
# Login accounts: client, petrova, manager, admin. Password: Demo123!
import bcrypt
from db import get_connection

PASSWORD = b'Demo123!'
HASH = bcrypt.hashpw(PASSWORD, bcrypt.gensalt()).decode('utf-8')
with get_connection() as conn:
    with conn.cursor() as cur:
        cur.execute('UPDATE users SET password_hash=%s', (HASH,))
        print(f'Пароль Demo123! установлен для {cur.rowcount} пользователей.')
