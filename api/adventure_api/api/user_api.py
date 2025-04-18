import json
import subprocess
import jwt
import os

from datetime import datetime, timedelta
from uuid import uuid4
from fastapi import APIRouter, Request, Header, HTTPException, Response
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from model import get_users, get_user_by_id, get_guest_user
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

@user_router.get('/api/v1/chatlog')
async def get_chatlog_route(request: Request):
    """GET /api/v1/chatlog

    Get the chat log.
    """
    user = request.user
    if not user or not user['is_admin']:
        raise HTTPException(403, 'You do not have permission to access this resource.')
    driver, conn = get_conn()
    if driver == 'sqlite':
        cur = conn.cursor()
        cur.execute('SELECT chatlog.id, user_id, message, timestamp, users.name FROM chatlog INNER JOIN users ON chatlog.user_id = users.id ORDER BY timestamp DESC')
        chatlog = cur.fetchall()
        cur.close()
    elif driver == 'postgres':
        cur = conn.cursor()
        cur.execute('SELECT chatlog.id, user_id, message, timestamp, users.name FROM chatlog INNER JOIN users ON chatlog.user_id = users.id ORDER BY timestamp DESC')
        chatlog = cur.fetchall()
        cur.close()
    
    chatlog = [
        dict(id=c[0], user=dict(id=c[1], name=c[4]), message=c[2], timestamp=c[3]) for c in chatlog
    ]

    return {
        'data': chatlog,
        'total': len(chatlog)
    }

@user_router.post('/api/v1/bugreports')
async def post_bugreport_route(request: Request):
    """POST /api/v1/bugreports

    Submit a bug report.
    """
    user = request.user
    if not user:
        raise HTTPException(403, 'You must be logged in to access this resource.')
    data = await request.json()
    if 'description' not in data:
        raise HTTPException(400, 'Missing required field: message')
    driver, conn = get_conn()
    report_id = str(uuid4())
    if driver == 'sqlite':
        cur = conn.cursor()
        cur.execute('INSERT INTO bug_report (id, user_id, description) VALUES (?, ?, ?)', (report_id, user['id'], data['description']))
        conn.commit()
        cur.close()
    elif driver == 'postgres':
        with conn.cursor() as cur:
            cur.execute('INSERT INTO bug_report (id, user_id, description) VALUES (%s, %s, %s)', (report_id, user['id'], data['description']))
        conn.commit()
    
    driver, conn = get_conn()
    if driver == 'sqlite':
        conn.execute(
            'INSERT INTO audit (id, user_id, classification, extra_data) VALUES (?, ?, ?, ?)',
            (str(uuid4()), user['id'], 'bug_report', f'{{"report_id": "{report_id}"}}'))
        conn.commit()
    elif driver == 'postgres':
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO audit (id, user_id, classification, extra_data) VALUES (%s, %s, %s, %s)',
                (str(uuid4()), user['id'], 'bug_report', f'{{"report_id": "{report_id}"}}'))
            conn.commit()
        conn.commit()
    
    return Response(status_code=201)


@user_router.get('/api/v1/audit')
async def get_audit_route(request: Request):
    """GET /api/v1/audit
    
    Get the audit log.
    """
    user = request.user
    if not user or not user['is_admin']:
        raise HTTPException(403, 'You do not have permission to access this resource.')
    driver, conn = get_conn()
    if driver == 'sqlite':
        cur = conn.cursor()
        cur.execute('SELECT audit.id, users.id, users.name, classification, extra_data, timestamp FROM audit INNER JOIN users ON audit.user_id = users.id ORDER BY timestamp DESC')
        audit = cur.fetchall()
        cur.close()
    elif driver == 'postgres':
        cur = conn.cursor()
        cur.execute('SELECT audit.id, users.id, users.name, classification, extra_data, timestamp FROM audit INNER JOIN users ON audit.user_id = users.id ORDER BY timestamp DESC')
        audit = cur.fetchall()
        cur.close()
    
    audit = [
        dict(id=a[0], user=dict(id=a[1], name=a[2]), classification=a[3], extra_data=json.dumps(a[4]), timestamp=a[5]) for a in audit
    ]

    return {
        'data': audit,
        'total': len(audit)
    }

@user_router.post('/api/v1/guest')
async def post_guest_route(request: Request):
    """POST /api/v1/guest
    
    Create or authenticate a guest user.
    """
    data = await request.json()
    
    guest_id = None
    guest_key = None
    
    if data:
        guest_id = data.get('guestId')
        guest_key = data.get('guestKey')
    
    user = get_guest_user(guest_id, guest_key)
    
    # Generate JWT token
    payload = {
        'user_id': user['id'],
        'email': user['email'],
        'is_admin': user['is_admin'],
        'exp': datetime.utcnow() + timedelta(days=14)
    }
    
    token = jwt.encode(payload, os.environ['CLIENT_SECRET'], algorithm='HS256')
    
    return {
        'token': token,
        'user': user
    }
