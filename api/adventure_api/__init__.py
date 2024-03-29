import asyncio
import threading
import logging
import shlex
import time
import jwt
import re
import os
from fastapi import Depends, FastAPI, HTTPException, WebSocket, Header, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from pydantic import BaseModel
from typing import Dict, Optional
from game import Character, BasicCommands, CommandHandler, World, WorldCommands
from user import check_password, get_user, register_user
from setup import setup_database

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b'


class RegisterRequest(BaseModel):
    email: str
    password: str


async def get_current_user(token: str = Depends(oauth2_scheme)):
    decoded_token = jwt.decode(token, CLIENT_SECRET, algorithms=['HS256'])
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
        'email': user[1],
        'is_admin': user[3]
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
    except (jwt.exceptions.DecodeError, jwt.exceptions.InvalidSignatureError):
        error = 'Incorrect email or password'
    if error or not user:
        await ws.send_json(dict(type='error', data=error))
        await ws.close()
        return
    ready = False
    already_logged_in = False
    for loaded_character in World._characters:
        if loaded_character._id == user['id']:
            already_logged_in = True
    character: Optional[Character] = None
    try:
        while True:
            data = await ws.receive_json()
            if data['type'] == 'ready' and not ready:
                ready = True
                if not already_logged_in:
                    character = Character(user['id'], ws)
                    if character.name:
                        await World.send_to_all(
                            'chat', '@lgr@{}@res@ has just logged in.\n', character.name)
                    World.add_player(character)
                    await character.handle_login()
                else:
                    await ws.send_json(dict(type='error', data='You are already logged in elsewhere.'))
            elif ready and character:
                try:
                    command = shlex.split(data['data'])
                except ValueError:
                    command = data['data'].split(" ")
                if len(data['data']) > 0 and data['data'].split(' ')[-1] == '':
                    command.append('')
                if data['type'] == 'autocomplete_suggest':
                    suggestion = character.command_handler.get_suggestion(
                        command)
                    await ws.send_json(dict(type='suggestion', data=suggestion))
                elif data['type'] == 'autocomplete_get':
                    suggestion = character.command_handler.get_suggestion(
                        command,
                        True)
                    await ws.send_json(dict(type='autocomplete', data=suggestion))
                elif data['type'] == 'game':
                    logger.info(
                        'handling command [%s] for [%s]',
                        data['data'],
                        character._name)
                    await character.command_handler.handle_input(command)
    except WebSocketDisconnect:
        pass
    except Exception as e:
        await ws.send_json(dict(type='error', data='An internal error has occurred.'))
        logging.exception(e)
        await ws.close()
    finally:
        if character:
            character.save_character()
            World.remove_player(character)

is_running = True


async def loop():
    logger.info('starting game loop')
    while is_running:
        try:
            now = time.perf_counter()
            await World.tick()

            now = time.perf_counter() - now
            if now > 600:
                now = 600
            await asyncio.sleep((600 - now) / 1000)
        except Exception as e:
            logger.error(f'error occurred in game loop')
            logger.exception(e)
    logger.info('ending game loop')

thread = threading.Thread(target=lambda: asyncio.run(loop()))


@app.on_event("startup")
def begin_game_loop():
    global is_running
    is_running = True
    setup_database()
    thread.start()


@app.on_event("shutdown")
def end_game_loop():
    global is_running
    is_running = False
    thread.join()
