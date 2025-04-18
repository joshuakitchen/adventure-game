from bcrypt import checkpw, hashpw, gensalt
from uuid import uuid4

from config import get_conn


def get_user_by_id(user_id):
    driver, conn = get_conn()
    if driver == 'sqlite':
        try:
            cur = conn.cursor()
            try:
                cur.execute(
                    'SELECT id, email, is_admin, name, state, x, z, additional_data FROM users WHERE id = ?',
                    [user_id])
                user_raw = curs.fetchone()
                if user_raw is None:
                    return None
                return dict(
                    id=user_raw[0],
                    email=user_raw[1],
                    is_admin=user_raw[2],
                    name=user_raw[3],
                    state=user_raw[4],
                    x=user_raw[5],
                    z=user_raw[6],
                    additional_data=user_raw[7]
                )
            finally:
                cur.close()
        finally:
            conn.close()
    elif driver == 'postgres':
        with conn.cursor() as curs:
            curs.execute(
                'SELECT id, email, is_admin, name, state, x, z, additional_data FROM users WHERE id = %s',
                [user_id])
            user_raw = curs.fetchone()
            if user_raw is None:
                return None
            return dict(
                id=user_raw[0],
                email=user_raw[1],
                is_admin=user_raw[2],
                name=user_raw[3],
                state=user_raw[4],
                x=user_raw[5],
                z=user_raw[6],
                additional_data=user_raw[7]
            )


def get_auth_user(email):
    driver, conn = get_conn()
    if driver == 'sqlite':
        try:
            cur = conn.cursor()
            try:
                cur.execute(
                    'SELECT id, email, password, is_admin FROM users WHERE email = ? AND is_guest = FALSE',
                    [email])
                return cur.fetchone()
            finally:
                cur.close()
        finally:
            conn.close()
    elif driver == 'postgres':
        with conn.cursor() as curs:
            curs.execute(
                'SELECT id, email, password, is_admin FROM users WHERE email = %s AND is_guest = FALSE',
                [email])
            return curs.fetchone()


def get_users():
    driver, conn = get_conn()
    if driver == 'sqlite':
        try:
            cur = conn.cursor()
            try:
                cur.execute('SELECT id, email, name, is_admin FROM users')
                return cur.fetchall()
            finally:
                cur.close()
        finally:
            conn.close()
    elif driver == 'postgres':
        with conn.cursor() as curs:
            curs.execute('SELECT id, email, name, is_admin FROM users')
            return curs.fetchall()


def check_password(expected, actual):
    if not isinstance(expected, bytes):
        expected = bytes(expected, 'utf-8')
    if not isinstance(actual, bytes):
        actual = bytes(actual, 'utf-8')
    return checkpw(expected, actual)


def register_user(email: str, password: str) -> str:
    new_id = str(uuid4())
    db_driver, conn = get_conn()
    if db_driver == 'sqlite':
        try:
            conn.execute('INSERT INTO users (id, email, password) VALUES (?, ?, ?)', [new_id, email, hashpw(password.encode('utf-8'), gensalt()).decode('utf-8')])
            conn.commit()
        finally:
            conn.close()
    elif db_driver == 'postgres':
        with conn.cursor() as cur:
            cur.execute('INSERT INTO users VALUES (%s, %s, %s)', [new_id, email, hashpw(
                password.encode('utf-8'), gensalt()).decode('utf-8')])
        conn.commit()
    return new_id


def get_guest_user(guest_id: str = None, guest_key: str = None):
    """
    Get or create a guest user.
    
    Args:
        guest_id: Optional guest ID (email)
        guest_key: Optional guest password
        
    Returns:
        Dictionary with guest user details including id, email, and is_guest flag
    """
    driver, conn = get_conn()
    
    if guest_id:
        # Try to retrieve existing guest user
        if driver == 'sqlite':
            try:
                cur = conn.cursor()
                try:
                    cur.execute(
                        'SELECT id, email, password, is_admin FROM users WHERE email = ? AND is_guest = TRUE',
                        [guest_id])
                    user = cur.fetchone()
                    if user and checkpw(guest_key.encode('utf-8'), user[2].encode('utf-8')):
                        return {
                            'id': user[0],
                            'email': user[1],
                            'is_admin': user[3],
                            'is_guest': True
                        }
                finally:
                    cur.close()
            finally:
                conn.close()
        elif driver == 'postgres':
            with conn.cursor() as curs:
                curs.execute(
                    'SELECT id, email, password, is_admin FROM users WHERE email = %s AND is_guest = TRUE',
                    [guest_id])
                user = curs.fetchone()
                if user:
                    if guest_key is not None and checkpw(guest_key.encode('utf-8'), user[2].encode('utf-8')):
                        return {
                            'id': user[0],
                            'email': user[1],
                            'is_admin': user[3],
                            'is_guest': True
                        }
                    elif guest_key is None:
                        return {
                            'id': user[0],
                            'email': user[1],
                            'is_admin': user[3],
                            'is_guest': True
                        }
                    
    
    # Create new guest user
    new_id = str(uuid4())
    if not guest_id:
        guest_id = f"guest_{new_id}@adventure.game"
    if not guest_key:
        guest_key = str(uuid4())
    
    if driver == 'sqlite':
        try:
            conn.execute(
                'INSERT INTO users (id, email, password, is_guest) VALUES (?, ?, ?, TRUE)',
                [new_id, guest_id, hashpw(guest_key.encode('utf-8'), gensalt()).decode('utf-8')])
            conn.commit()
        finally:
            conn.close()
    elif driver == 'postgres':
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO users (id, email, password, is_guest) VALUES (%s, %s, %s, TRUE)',
                [new_id, guest_id, hashpw(guest_key.encode('utf-8'), gensalt()).decode('utf-8')])
        conn.commit()
    
    return {
        'id': new_id,
        'email': guest_id,
        'is_admin': False,
        'is_guest': True
    }
