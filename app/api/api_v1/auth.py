from typing import Optional, Union

from fastapi import APIRouter, Cookie, Depends, Request
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from app import deps
from app.authentication import decode_token, oauth
from app.config import settings

router = APIRouter()


@router.get("/login")
async def login(
    request: Request,
    redirect_on_callback: str = f"{settings.BASE_PATH}/docs",
    current_user: Union[dict, None] = Depends(deps.get_current_user),
):
    
    if not current_user:
        # redirect_uri = request.url_for('callback')
        redirect_uri = f"{settings.SERVER_HOST}/callback"
        response = await oauth.smartcommunitylab.authorize_redirect(request, redirect_uri)
        response.set_cookie(
            key="redirect_on_callback",
            value=redirect_on_callback,
            httponly=True,
            # TODO: False if dev, true if prod
            secure=False
        )
        return response
    else:
        print("user already logged in")
        # if user already logged in, redirect to redirect_on_callback
        return RedirectResponse(redirect_on_callback)

@router.get("/callback")
async def callback(request: Request, redirect_on_callback: Optional[str] = Cookie(None)):
    try:
        token = await oauth.smartcommunitylab.authorize_access_token(request)
        response = RedirectResponse(redirect_on_callback)        
        
        response.set_cookie(
            key="auth_token",
            value=token["access_token"],
            expires=token["expires_in"],
            httponly=True,
            # TODO: False if dev, true if prod
            secure=False
        )
        
        response.delete_cookie(key="redirect_on_callback")
        # user = await oauth.smartcommunitylab.parse_id_token(request, token)
        # print(user)
        return response
    except Exception as e:
        return e


@router.get("/logout")
async def logout(redirect_on_callback: str = settings.BASE_PATH or "/"):
    response = RedirectResponse(url=redirect_on_callback)
    response.delete_cookie(key="auth_token")
    # TODO: get token and call revocation
    return response
