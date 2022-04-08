from typing import Optional, Union

from fastapi import APIRouter, Cookie, Depends, Request
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from app import deps, crud
from app.authentication import oauth, url
from app.config import settings
from app.database import AsyncIOMotorCollection, get_collection
from urllib.parse import quote_plus, urlencode

router = APIRouter()


@router.get("/login")
async def login(
    request: Request,
    redirect_on_callback: str = f"{settings.COMPLETE_SERVER_NAME}/docs",
    current_user: Union[dict, None] = Depends(deps.get_current_user),
):
    print(f"{settings.COMPLETE_SERVER_NAME}/docs")
    if not current_user:
        # redirect_uri = request.url_for('callback')
        redirect_uri = f"{settings.COMPLETE_SERVER_NAME}/callback"
        response = await oauth.smartcommunitylab.authorize_redirect(request, redirect_uri)
        request.session["redirect_on_callback"] = redirect_on_callback
        return response
    else:
        print("user already logged in")
        # if user already logged in, redirect to redirect_on_callback
        return RedirectResponse(redirect_on_callback)


@router.get("/callback")
async def callback(request: Request, collection: AsyncIOMotorCollection = Depends(get_collection)):
    try:
        token = await oauth.smartcommunitylab.authorize_access_token(request)
        await crud.get_or_create(collection, token["access_token"])
        
        response = RedirectResponse(request.session.get("redirect_on_callback", "/noredirect"),)        
        request.session["id_token"] = token["id_token"]
        response.set_cookie(
            key="auth_token",
            value=token["access_token"],
            expires=token["expires_in"],
            httponly=True,
            samesite='strict',
            domain=settings.SERVER_NAME,
            secure=settings.PRODUCTION_MODE,
        )
        # user = await oauth.smartcommunitylab.parse_id_token(request, token)
        # print(user)
        return response
    except Exception as e:
        raise e


@router.get("/logout")
async def logout(request: Request, redirect_on_callback: str = settings.COMPLETE_SERVER_NAME):
    url = settings.SERVER_URL + "/endsession?" + urlencode(
            {
                "id_token_hint": request.session.get("id_token", None),
                "post_logout_redirect_uri": redirect_on_callback
            },
            
        )
    print(url)
    response = RedirectResponse(url
    )
    response.delete_cookie(key="auth_token")
    return response
