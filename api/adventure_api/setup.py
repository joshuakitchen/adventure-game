from config import get_conn

import logging
logger = logging.getLogger(__name__)


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
                email VARCHAR(255) NOT NULL UNIQUE,
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


def create_chatlog_table():
    """Creates the chatlog table if it doesn't exist"""
    driver, conn = get_conn()
    if driver == 'sqlite':
        try:
            conn.execute(
                '''CREATE TABLE IF NOT EXISTS chatlog (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )'''
                )
            conn.commit()
        finally:
            conn.close()
    elif driver == 'postgres':
        with conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS chatlog (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )''')
        conn.commit()

def create_audit_table():
    """Creates the audit table if it doesn't exist"""
    driver, conn = get_conn()
    if driver == 'sqlite':
        try:
            conn.execute(
                '''CREATE TABLE IF NOT EXISTS audit (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                classification VARCH(40) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                extra_data TEXT DEFAULT '{}'
                )'''
                )
            conn.commit()
        finally:
            conn.close()
    elif driver == 'postgres':
        with conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS audit (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                classification VARCHAR(40) NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                extra_data TEXT DEFAULT '{}'
                )''')
        conn.commit()


def create_bug_report_table():
    """Creates the bug_report table if it doesn't exist"""
    driver, conn = get_conn()
    if driver == 'sqlite':
        try:
            conn.execute(
                '''CREATE TABLE IF NOT EXISTS bug_report (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                description TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                severity INT DEFAULT -1,
                is_resolved BOOLEAN DEFAULT FALSE
                )'''
                )
            conn.commit()
        finally:
            conn.close()
    elif driver == 'postgres':
        with conn.cursor() as cur:
            cur.execute('''CREATE TABLE IF NOT EXISTS bug_report (
                id VARCHAR(36) PRIMARY KEY,
                user_id VARCHAR(36) NOT NULL,
                description TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                severity INT DEFAULT -1,
                is_resolved BOOLEAN DEFAULT FALSE
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
            version_obj = cur.fetchone()

            version = version_obj[0] if version_obj else 0

            if not version_obj:
                cur.execute('''ALTER TABLE users
                            ADD COLUMN IF NOT EXISTS date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            ADD COLUMN IF NOT EXISTS last_login TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            ADD COLUMN IF NOT EXISTS last_played TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            ADD COLUMN IF NOT EXISTS last_session_id VARCHAR(36) DEFAULT NULL''')

                cur.execute("INSERT INTO db_version (id) VALUES (1)")
                conn.commit()
            elif version <= 1:
                cur.execute('''ALTER TABLE users
                            DROP CONSTRAINT IF EXISTS users_email_key,
                            ADD COLUMN IF NOT EXISTS is_guest BOOLEAN DEFAULT FALSE,
                            ALTER COLUMN email DROP NOT NULL,
                            ALTER COLUMN password DROP NOT NULL''')

                cur.execute("INSERT INTO db_version (id) VALUES (2)")
                conn.commit()

            old_version = version
            cur.execute("SELECT id, timestamp FROM db_version ORDER BY id DESC LIMIT 1")
            version = cur.fetchone()
            version = version[0] if version else 0
            if version != old_version:
                logger.info('migrated from %s to %s', old_version, version)


def setup_database():
    create_version_table()
    create_user_table()
    create_chatlog_table()
    create_audit_table()
    create_bug_report_table()

    migrate()
