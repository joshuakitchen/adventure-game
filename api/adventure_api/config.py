import os
import psycopg2
import sqlite3
from typing import Any


def get_db_driver() -> str:
    return os.environ.get('DB_DRIVER', 'sqlite')


def get_conn() -> Any:
    if getattr(get_conn, 'connection', None):
        return getattr(get_conn, 'connection')
    db_driver = get_db_driver()
    if db_driver == 'sqlite':
        return ('sqlite', sqlite3.connect(
            os.environ.get('DB_FILE', ':memory:')))
    elif db_driver == 'postgres':
        conn = ('postgres', psycopg2.connect(
            host=os.environ.get('DB_HOST'),
            database=os.environ.get('DB_DATABASE'),
            user=os.environ.get('DB_USER'),
            password=os.environ.get('DB_PASSWORD')))
        setattr(get_conn, 'connection', conn)
        return conn
    else:
        raise ValueError(f'unsupported database driver {db_driver}')
