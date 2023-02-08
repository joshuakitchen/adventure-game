from adventure_api.setup import get_conn

if __name__ == '__main__':
    driver, conn = get_conn()
    try:
        with conn.cursor() as cur:
            cur.execute('SELECT id, email, state FROM users')
            for user in cur.fetchall():
                print(f'{user[0]} | {user[1]} | {user[2]}')
    finally:
        conn.close()
