from typing import Generator

from fastapi import Depends, HTTPException, Request
from app.authentication import decode_token
from app import crud

def get_token_in_cookie(request):
    try:
        return request.cookies.get("auth_token")
    except:
        return None

def get_token_in_header(request):
    try:
        return request.headers.get('authorization').replace("Bearer ", "")
    except:
        return None

def get_current_token(
    request: Request
) -> dict:
        state = request.state._state
        return state["token"]

async def get_current_user(
    request: Request,
) -> dict:
    try:
        token = get_token_in_cookie(request) or get_token_in_header(request)
        # gets user_data from state (see AuthMiddleware)
        if token:
            token_info = decode_token(token)
            return await crud.get_or_create(token_info)
        return None
    except Exception as e:
        print(str(e))
        return None

def get_current_active_user(
    current_user: dict = Depends(get_current_user),
) -> dict:
    # calls get_current_user, and if nothing is returned, raises Not authenticated exception
    if not current_user:
        raise HTTPException(status_code=403, detail="Not authenticated")
    return current_user


def get_current_active_superuser(
    current_user: dict = Depends(get_current_user),
) -> dict:
    if True:
        raise HTTPException(
            status_code=403, detail="The user doesn't have enough privileges"
        )
    return current_user
