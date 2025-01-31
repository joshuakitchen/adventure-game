from config import get_conn


def create_version_table():
    """Creates the version table if it doesn't exist"""
    driver, conn = get_conn()
    if driver == 'sqlite':
        try:
            conn.execute(
                '''CREATE TABLE IF NOT EXISTS db_version (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )'''
                )
            conn.commit()
        finally:
            conn.close()
    elif driver == 'postgres':
        with conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS db_version (
                id INTEGER PRIMARY KEY,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
        conn.commit()


def create_user_table():
    """Creates the user table if it doesn't exist"""
    driver, conn = get_conn()
    if driver == 'sqlite':
        try:
            conn.execute(
                '''CREATE TABLE IF NOT EXISTS users (
                    id VARCHAR(36) NOT NULL PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password TEXT NOT NULL,
                    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_admin BOOLEAN DEFAULT FALSE,
                    name VARCHAR(20),
                    state VARCHAR(40) DEFAULT \'intro\',
                    x INT DEFAULT 0,
                    z INT DEFAULT 0,
                    last_session_id VARCHAR(36) DEFAULT NULL,
                    additional_data DEFAULT \'{}\'
                )''')
            conn.commit()
        finally:
            conn.close()
    elif driver == 'postgres':
        with conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS users (
                id VARCHAR(36) NOT NULL PRIMARY KEY,
                email VARCHAR(255)NOT NULL UNIQUE,
                password TEXT NOT NULL,
                date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_admin BOOLEAN DEFAULT FALSE,
                name VARCHAR(20),
                state VARCHAR(40) DEFAULT 'intro',
                x INT DEFAULT 0,
                z INT DEFAULT 0,
                last_session_id VARCHAR(36) DEFAULT NULL,
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


def migrate():
    """Migrate the database"""
    driver, conn = get_conn()
    if driver == 'sqlite':
        try:
            conn.execute("SELECT id, timestamp FROM db_version ORDER BY id DESC LIMIT 1")
            version = conn.fetchone()

            print(version)
        finally:
            conn.close()
    elif driver == 'postgres':
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM db_version ORDER BY id DESC LIMIT 1")
            version = cur.fetchone()[0]

            if not version:
                cur.execute('''ALTER TABLE users
                            ADD COLUMN IF NOT EXISTS date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            ADD COLUMN IF NOT EXISTS last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            ADD COLUMN IF NOT EXISTS last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            ADD COLUMN IF NOT EXISTS last_session_id VARCHAR(36) DEFAULT NULL''')

                cur.execute("INSERT INTO db_version (id) VALUES (1)")
                conn.commit()
                cur.execute("SELECT id, timestamp FROM db_version ORDER BY id DESC LIMIT 1")
                version = cur.fetchone()
                print('new version', version)


def setup_database():
    create_user_table()
    create_version_table()

    migrate()
