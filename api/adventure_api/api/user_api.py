from fastapi import APIRouter, Request, Header, HTTPException
from model import get_users
from game import World

user_router = APIRouter()

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
