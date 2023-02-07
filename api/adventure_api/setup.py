from bcrypt import hashpw, gensalt
from uuid import uuid4

from .config import get_conn

def create_character_table():
  conn = get_conn()
  try:
    conn.execute('CREATE TABLE IF NOT EXISTS characters (id VARCHAR(36) NOT NULL, owner_id VARCHAR(36) NOT NULL, state TEXT NOT NULL, FOREIGN KEY (owner_id) REFERENCES users(id))')
    conn.commit()
  finally:
    conn.close()

def create_user_table():
  conn = get_conn()
  try:
    conn.execute('CREATE TABLE IF NOT EXISTS users (id VARCHAR(36) NOT NULL, email VARCHAR(255) NOT NULL UNIQUE, password TEXT NOT NULL)')
    conn.commit()
  finally:
    conn.close()

def setup_database():
  create_user_table()
  create_character_table()
