import sqlite3

def get_conn() -> sqlite3.Connection:
  return sqlite3.connect('./data/adventure.db')
