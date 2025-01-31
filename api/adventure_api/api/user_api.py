import subprocess

from datetime import datetime
from fastapi import APIRouter, Request, Header, HTTPException, Response
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel
from model import get_users, get_user_by_id
from game import World
from setup import get_conn

user_router = APIRouter()

class PutUserRequest(BaseModel):
    additional_data: str

def fmt_sql_val(val):
    if val is None:
        return 'NULL'
    if isinstance(val, str):
        return f"'{val}'"
    if isinstance(val, datetime):
        return f"'{val.isoformat()}'"
    return str(val)

@user_router.get('/api/v1/db')
async def get_db_dump(request: Request) -> Response:
    """GET /api/v1/db
    
    Get a dump of the database, for migration from the app platform."""
    user = request.user
    if not user or not user['is_admin']:
        raise HTTPException(403, 'You do not have permission to access this resource.')
    
    sql_cmd = ''

    driver, conn = get_conn()
    if driver == 'sqlite':
        raise HTTPException(501, 'Not implemented for SQLite')
    elif driver == 'postgres':
        with conn.cursor() as cur:
            cur.execute('SELECT * FROM users')
            users = cur.fetchall()
            for user in users:
                sql_cmd += f"INSERT INTO users VALUES ({', '.join([fmt_sql_val(x) for x in user])});"
                sql_cmd += '\n\n'
            cur.execute('SELECT * FROM db_version')
            db_version = cur.fetchall()
            for version in db_version:
                sql_cmd += f"INSERT INTO db_version VALUES ({', '.join([fmt_sql_val(x) for x in version])});"
                sql_cmd += '\n\n'

    return PlainTextResponse(content=sql_cmd)



@user_router.get('/api/v1/users')
async def get_users_route(request: Request):
    """GET /api/v1/users

    Get all users in the system.
    """
    user = request.user
    if not user or not user['is_admin']:
        raise HTTPException(403, 'You do not have permission to access this resource.')
    users = [
        dict(id=u[0], email=u[1], name=u[2], location='Offline' if World.get_player(u[2]) is None else World.get_player(u[2]).coordinate_str, is_admin=u[3]) for u in get_users()
    ]

    return {
        'data': users,
        'total': len(users)
    }

@user_router.get('/api/v1/users/{user_id}')
async def get_user_route(user_id: str, request: Request):
    """GET /api/v1/users/{user_id}

    Get a user by ID.
    """
    user = request.user
    if not user or not user['is_admin']:
        raise HTTPException(403, 'You do not have permission to access this resource.')
    user = get_user_by_id(user_id)

    if user is None:
        raise HTTPException(404, 'User not found.')

    return user

@user_router.put('/api/v1/users/{user_id}')
async def put_user_route(user_id: str, put_req: PutUserRequest, request: Request):
    """PUT /api/v1/users/{user_id}

    Update a user by ID.
    """
    user = request.user
    if not user or not user['is_admin']:
        raise HTTPException(403, 'You do not have permission to access this resource.')
    user = get_user_by_id(user_id)

    if user is None:
        raise HTTPException(404, 'User not found.')
    
    driver, conn = get_conn()
    if driver == 'sqlite':
        raise HTTPException(501, 'Not implemented for SQLite')
    elif driver == 'postgres':
        cur = conn.cursor()
        cur.execute('UPDATE users SET additional_data = %s WHERE id = %s', (put_req.additional_data, user_id))
        conn.commit()
        cur.close()
    
    user = get_user_by_id(user_id)

    return user
