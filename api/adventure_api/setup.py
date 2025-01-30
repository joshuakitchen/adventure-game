from config import get_conn


def create_user_table():
    """Creates the user table if it doesn't exist"""
    driver, conn = get_conn()
    if driver == 'sqlite':
        try:
            conn.execute(
                'CREATE TABLE IF NOT EXISTS users (id VARCHAR(36) NOT NULL PRIMARY KEY, email VARCHAR(255) NOT NULL UNIQUE, password TEXT NOT NULL, is_admin BOOLEAN DEFAULT FALSE, name VARCHAR(20), state VARCHAR(40) DEFAULT \'intro\', x INT DEFAULT 0, z INT DEFAULT 0, additional_data DEFAULT \'{}\')')
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

def create_audit_table():
    """Creates the audit table if it doesn't exist"""
    driver, conn = get_conn()
    if driver == 'sqlite':
        try:
            conn.execute(
                '''CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id VARCHAR(36) NOT NULL,
                action VARCHAR(255) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )'''
                )
            conn.commit()
        finally:
            conn.close()
    elif driver == 'postgres':
        with conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS audit (
                id SERIAL PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                action VARCHAR(255) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
        conn.commit()


def setup_database():
    create_user_table()
