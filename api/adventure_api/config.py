import os
import psycopg2
import sqlite3
from typing import Any


def get_db_driver() -> str:
    return os.environ.get('DB_DRIVER', 'sqlite')


def get_conn() -> Any:
    db_driver = get_db_driver()
    if getattr(get_conn, 'connection', None):
        conn = getattr(get_conn, 'connection')
        # Check if the connection is still open
        if db_driver == 'postgres':
            try:
                cur = conn[1].cursor()
                cur.execute('SELECT 1')
            except (psycopg2.OperationalError, psycopg2.InterfaceError):
                setattr(get_conn, 'connection', None)
                return get_conn()

        return conn
    if db_driver == 'sqlite':
        return ('sqlite', sqlite3.connect(
            os.environ.get('DB_FILE', ':memory:')))
    elif db_driver == 'postgres':
        conn = ('postgres', psycopg2.connect(
            host=os.environ.get('DB_HOST', 'localhost'),
            database=os.environ.get('DB_DATABASE', 'pg'),
            user=os.environ.get('DB_USER', 'postgres'),
            password=os.environ.get('DB_PASSWORD'),
            port=os.environ.get('DB_PORT', 5432),
            sslmode=os.environ.get('DB_SSLMODE', None)))
        setattr(get_conn, 'connection', conn)
        return conn
    else:
        raise ValueError(f'unsupported database driver {db_driver}')
