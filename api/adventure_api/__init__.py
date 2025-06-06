import asyncio
import threading
import logging
import shlex
import time
from uuid import uuid4
import jwt
import re
import os
from fastapi import Depends, FastAPI, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from config import get_conn
from game import Character, World
from model import check_password, get_auth_user, register_user
from setup import setup_database
from starlette.middleware.authentication import AuthenticationMiddleware
from auth import BearerTokenBackend
from api import user_router
from game.data import load_data
from game.sentence import SentenceHandler, SentenceParseError

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


@app.get('/health')
async def health_check():
    return {"status": "healthy"}


@app.post('/register')
async def register(req: RegisterRequest):
    if not re.fullmatch(email_regex, req.email):
        raise HTTPException(400, 'Email is not a valid email address.')
    if len(req.password) < 8:
        raise HTTPException(400, 'Password must be above 8 characters.')
    u = get_auth_user(req.email)
    if u:
        raise HTTPException(403, 'That email is already taken')
    user_id = register_user(req.email, req.password)

    driver, conn = get_conn()
    if driver == 'sqlite':
        conn.execute(
            'INSERT INTO audit (id, user_id, classification) VALUES (?, ?, ?)',
            (str(uuid4()), user_id, 'register'))
        conn.commit()
    elif driver == 'postgres':
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO audit (id, user_id, classification) VALUES (%s, %s, %s)',
                (str(uuid4()), user_id, 'register'))
            conn.commit()
        conn.commit()

    return {
        'success': True
    }


@app.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.client_id != CLIENT_ID and form_data.client_id != CLIENT_SECRET:
        raise HTTPException(status_code=400, detail='Invalid client')
    user = get_auth_user(form_data.username)
    if not user:
        raise HTTPException(
            status_code=400,
            detail='Incorrect email or password.')
    if not check_password(form_data.password, user[2]):
        raise HTTPException(
            status_code=400,
            detail='Incorrect email or password.')
    
    driver, conn = get_conn()
    if driver == 'sqlite':
        conn.execute(
            'INSERT INTO audit (id, user_id, classification) VALUES (?, ?, ?)',
            (str(uuid4()), user[0], 'login'))
        conn.commit()
    elif driver == 'postgres':
        with conn.cursor() as cur:
            cur.execute(
                'INSERT INTO audit (id, user_id, classification) VALUES (%s, %s, %s)',
                (str(uuid4()), user[0], 'login'))
            conn.commit()
        conn.commit()

    return {
        'access_token': jwt.encode({'type': 'access_token', 'user_id': user[0], 'email': user[1], 'client_id': CLIENT_ID}, CLIENT_SECRET, algorithm='HS256'),
        'refresh_token': jwt.encode({'type': 'refresh_token', 'user_id': user[0], 'email': user[1], 'client_id': CLIENT_ID}, CLIENT_SECRET, algorithm='HS256'),
        'user_id': user[0],
        'email': user[1],
        'is_admin': user[3]
    }


@app.websocket('/play')
async def play(ws: WebSocket, session: str):
    await ws.accept()
    user = ws.user
    # Check if user is an authenticated user (not UnauthenticatedUser)
    if not user or not hasattr(user, 'get'):
        await ws.send_json(dict(type='error', data='You must be logged in to play.'))
        await ws.close()
        return
    logging.info('user [%s] connected', user.get('id'))
    for loaded_character in World._characters:
        if loaded_character._id == user.get('id'):
            if loaded_character._session_id != session:
                await loaded_character._ws.send_json(dict(type='error', data='You have logged in elsewhere, please refresh to reconnect here.', retry=False))
            await loaded_character._ws.close()
            break
    character: Optional[Character] = None
    try:
        character = World.get_player_by_id(user.get('id'), True)
        if not character:
            character = Character(user.get('id'), ws, session)
            if character.name:
                await World.send_to_all('chat', '@lgr@{}@res@ has just logged in.\n', character.name)
            World.add_player(character)
            await character.handle_login()
        else:
            continue_session = character._session_id == session
            character._ws = ws
            character._session_id = session
            character._disconnected = False
            World.add_player(character)
            if continue_session:
                await character.handle_login(send_motd=False)
            else:
                await character.handle_login()

        while True:
            data = await ws.receive_json()
            try:
                command = shlex.split(data['data'])
            except ValueError:
                command = data['data'].split(" ")
            except KeyError:
                command = ['']
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
                if character._settings.get('input', 'command') == 'command':
                    logger.info(
                        'handling command [%s] for [%s]',
                        data['data'],
                        character._name)
                    await character.command_handler.handle_input(command)
                elif character._settings.get('input', 'command') == 'sentence':
                    logger.info(
                        'handling sentence [%s] for [%s]',
                        data['data'],
                        character._name)
                    try:
                        await SentenceHandler.parse_sentence(character, data['data'])
                    except SentenceParseError as e:
                        await ws.send_json(dict(type='game', data=str(e)))
                else:
                    logging.error('unknown input type [%s]', character._settings.get('input', 'command'))
            elif data['type'] == 'ping':
                await ws.send_json(dict(type='pong', data=''))
    except WebSocketDisconnect:
        logging.info('websocket [%s] disconnected', user['id'])
    except Exception as e:
        await ws.send_json(dict(type='error', data='An internal error has occurred.'))
        logging.exception(e)
        await ws.close()
    finally:
        if character:
            character._disconnected = True
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
    logger.info('saving awaiting characters loop')
    for c in World._characters:
        c.save_character()
    for c in World._awaiting_characters:
        c[0].save_character()
    logger.info('ending game loop')

thread = threading.Thread(target=lambda: asyncio.run(loop()))


@app.on_event("startup")
def begin_game_loop():
    load_data()
    SentenceHandler.load_terms()

    app.include_router(user_router)
    app.add_middleware(AuthenticationMiddleware, backend=BearerTokenBackend())

    global is_running
    is_running = True
    setup_database()
    thread.start()


@app.on_event("shutdown")
def end_game_loop():
    global is_running
    is_running = False
    thread.join()
