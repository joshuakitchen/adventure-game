from starlette.authentication import AuthenticationBackend, AuthCredentials
from fastapi.security.utils import get_authorization_scheme_param
from model import get_auth_user, get_guest_user
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
            user_id = decoded_token['user_id']
            email = decoded_token['email']
            
            # First try regular user authentication
            auth_user = get_auth_user(email)
            if auth_user:
                user = {'id': auth_user[0], 'email': auth_user[1], 'is_admin': auth_user[3]}
                return AuthCredentials(["authenticated"]), user
            
            # Fallback to guest user authentication if regular auth fails
            guest_user = get_guest_user(email)
            if guest_user:
                return AuthCredentials(["authenticated", "guest"]), guest_user
                
            # Authentication failed completely
            return None
                
        except (ValueError, jwt.PyJWTError) as e:
            logging.exception(e)
            return None
