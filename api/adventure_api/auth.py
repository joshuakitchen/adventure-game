from starlette.authentication import AuthenticationBackend, AuthCredentials
from fastapi.security.utils import get_authorization_scheme_param
from model import get_auth_user
import jwt
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CLIENT_SECRET = os.environ['CLIENT_SECRET']

class BearerTokenBackend(AuthenticationBackend):
    async def authenticate(self, conn):
        if "Authorization" not in conn.headers:
            return None
        
        auth = conn.headers["Authorization"]
        try:
            scheme, param = get_authorization_scheme_param(auth)
            if scheme.lower() != "bearer":
                return None
            decoded_token = jwt.decode(param, CLIENT_SECRET, algorithms=['HS256'])
            user = {'id': decoded_token['user_id'], 'email': decoded_token['email']}
        except (ValueError, jwt.PyJWTError) as e:
            logging.exception(e)
            return None
        
        user = get_auth_user(user['email'])
        if not user:
            return None
        
        user = {'id': user[0], 'email': user[1], 'is_admin': user[3]}
        
        return AuthCredentials(["authenticated"]), user
