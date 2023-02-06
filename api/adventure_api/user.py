from bcrypt import checkpw

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
  return checkpw(bytes(expected, 'utf-8'), bytes(actual, 'utf-8'))
