import uvicorn
import jwt
from fastapi import Depends, FastAPI, HTTPException, WebSocket, Header, WebSocketDisconnect
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.security.utils import get_authorization_scheme_param
from .adventure import Adventure
from .command import CommandHandler
from .setup import setup_database
from .user import check_password, get_user

CLIENT_ID = '4752871f-71c5-4940-8c1e-bee3be614c63'
CLIENT_SECRET = '0f2321742fc62e3390e9b1d2161be5665652a1c9e1bb781f012edf8a3f1176721e257a4866703cce'

app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='token')

async def get_current_user(token: str = Depends(oauth2_scheme)):
  try:
    decoded_token = jwt.decode(token, CLIENT_SECRET, algorithms=['HS256'])
  except jwt.InvalidSignatureError:
    raise HTTPException(status_code=400, detail='Invalid token')
  return {'id': decoded_token['user_id'], 'email': decoded_token['email']}

@app.post('/token')
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
  if form_data.client_id != CLIENT_ID and form_data.client_id != CLIENT_SECRET:
    raise HTTPException(status_code=400, detail='Invalid client')
  user = get_user(form_data.username)
  if not user:
    raise HTTPException(status_code=400, detail='Incorrect email or password.')
  if not check_password(form_data.password, user[2]):
    raise HTTPException(status_code=400, detail='Incorrect email or password.')
  return {
    'access_token': jwt.encode({ 'type': 'access_token', 'user_id': user[0], 'email': user[1], 'client_id': CLIENT_ID }, CLIENT_SECRET, algorithm='HS256'),
    'refresh_token': jwt.encode({ 'type': 'refresh_token', 'user_id': user[0], 'email': user[1], 'client_id': CLIENT_ID }, CLIENT_SECRET, algorithm='HS256'),
    'user_id': user[0],
    'email': user[1]
  }

@app.websocket('/play')
async def play(ws: WebSocket, authorization = Header()):
  scheme, param = get_authorization_scheme_param(authorization)
  if scheme != 'Bearer':
    raise HTTPException(status_code=400, detail='Incorrect email or password.')
  user = await get_current_user(param)
  await ws.accept()
  ready = False
  adventure = Adventure(ws, user['id'])
  command_handler = CommandHandler(adventure)
  try:
    while True:
        data = await ws.receive_text()
        if data == 'ready' and not ready:
          ready = True
          await ws.send_text(adventure.get_intro())
        elif ready:
          await command_handler.handle_input(data)
  except WebSocketDisconnect:
    pass
