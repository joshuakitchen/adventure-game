import logging
import jwt
import re
from fastapi import Depends, FastAPI, HTTPException, WebSocket, Header, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel
from typing import Dict, Optional
from .game import Character, CommandHandler, World
from .user import check_password, get_user, register_user

CLIENT_ID = '4752871f-71c5-4940-8c1e-bee3be614c63'
CLIENT_SECRET = '0f2321742fc62e3390e9b1d2161be5665652a1c9e1bb781f012edf8a3f1176721e257a4866703cce'

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


class RegisterRequest(BaseModel):
    email: str
    password: str


async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        decoded_token = jwt.decode(token, CLIENT_SECRET, algorithms=['HS256'])
    except jwt.InvalidSignatureError:
        raise HTTPException(status_code=400, detail='Invalid token')
    return {'id': decoded_token['user_id'], 'email': decoded_token['email']}


@app.post('/register')
async def register(req: RegisterRequest):
    if not re.fullmatch(email_regex, req.email):
        raise HTTPException(400, 'Email is not a valid email address.')
    if len(req.password) < 8:
        raise HTTPException(400, 'Password must be above 8 characters.')
    u = get_user(req.email)
    if u:
        raise HTTPException(403, 'That email is already taken')
    register_user(req.email, req.password)
    return {
        'success': True
    }


@app.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.client_id != CLIENT_ID and form_data.client_id != CLIENT_SECRET:
        raise HTTPException(status_code=400, detail='Invalid client')
    user = get_user(form_data.username)
    if not user:
        raise HTTPException(
            status_code=400,
            detail='Incorrect email or password.')
    if not check_password(form_data.password, user[2]):
        raise HTTPException(
            status_code=400,
            detail='Incorrect email or password.')
    return {
        'access_token': jwt.encode({'type': 'access_token', 'user_id': user[0], 'email': user[1], 'client_id': CLIENT_ID}, CLIENT_SECRET, algorithm='HS256'),
        'refresh_token': jwt.encode({'type': 'refresh_token', 'user_id': user[0], 'email': user[1], 'client_id': CLIENT_ID}, CLIENT_SECRET, algorithm='HS256'),
        'user_id': user[0],
        'email': user[1]
    }


@app.websocket('/play')
async def play(ws: WebSocket, authorization=Header()):
    await ws.accept()
    error = None
    scheme, param = get_authorization_scheme_param(authorization)
    if scheme != 'Bearer':
        error = 'Incorrect email or password'
    user: Optional[Dict[str, str]] = None
    try:
        user = await get_current_user(param)
    except jwt.exceptions.DecodeError:
        error = 'Incorrect email or password'
    if error or not user:
        await ws.send_json(dict(type='error', data=error))
        await ws.close()
        return
    ready = False
    character = Character(user['id'], ws)
    command_handler = CommandHandler(character)
    try:
        while True:
            data = await ws.receive_json()
            if data['type'] == 'ready' and not ready:
                ready = True
                World.add_player(character)
                await character.handle_login()
            elif ready:
                if data['type'] == 'autocomplete':
                    await command_handler.handle_autocomplete_request(data['data'].split(' '))
                elif data['type'] == 'game':
                    await command_handler.handle_input(data['data'].split(' '))
    except WebSocketDisconnect:
        pass
    except Exception as e:
        logging.exception(e)
        await ws.close()
    finally:
        character.save_character()
        World.remove_player(character)
