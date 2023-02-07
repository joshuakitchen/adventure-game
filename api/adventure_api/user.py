from bcrypt import checkpw, hashpw, gensalt
from fastapi import HTTPException
from uuid import uuid4

from .config import get_conn

def get_user(email):
  conn = get_conn()
  try:
    cur = conn.cursor()
    try:
      cur.execute('SELECT id, email, password FROM users WHERE email = ?', [email])
      return cur.fetchone()
    finally:
      cur.close()
  finally:
    conn.close()

def check_password(expected, actual):
  if not isinstance(expected, bytes):
    expected = bytes(expected, 'utf-8')
  if not isinstance(actual, bytes):
    actual = bytes(actual, 'utf-8')
  return checkpw(expected, actual)

def register_user(email: str, password: str):
  conn = get_conn()
  try:
    conn.execute('INSERT INTO users VALUES (?, ?, ?)', [str(uuid4()), email, hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')])
    conn.commit()
  finally:
    conn.close()
