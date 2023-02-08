from bcrypt import hashpw, gensalt
from uuid import uuid4

from .config import get_conn


def create_user_table():
    driver, conn = get_conn()
    if driver == 'sqlite':
        try:
            conn.execute(
                'CREATE TABLE IF NOT EXISTS users (id VARCHAR(36) NOT NULL PRIMARY KEY, email VARCHAR(255) NOT NULL UNIQUE, password TEXT NOT NULL, state TEXT)')
            conn.commit()
        finally:
            conn.close()
    elif driver == 'postgres':
        with conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                email VARCHAR(255)NOT NULL UNIQUE,
                password TEXT NOT NULL,
                is_admin BOOLEAN DEFAULT FALSE,
                name VARCHAR(20),
                state VARCHAR(40) DEFAULT 'intro',
                x INT DEFAULT 0,
                z INT DEFAULT 0,
                additional_data TEXT DEFAULT '{}'
                )''')
        conn.commit()


def setup_database():
    create_user_table()
