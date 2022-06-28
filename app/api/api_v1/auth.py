from typing import Optional, Union

from fastapi import APIRouter, Cookie, Depends, Request
from fastapi.responses import RedirectResponse
from starlette.requests import Request

from app import deps, crud
from app.authentication import oauth, url
from app.config import settings
from app.database import AsyncIOMotorCollection, get_collection
from urllib.parse import quote_plus, urlencode
import datetime

router = APIRouter()


@router.get("/login")
async def login(
    request: Request,
    redirect_on_callback: str = f"{settings.COMPLETE_SERVER_NAME}/docs",
    current_user: Union[dict, None] = Depends(deps.get_current_user),
):
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
        await crud.get_or_create(collection, token["access_token"], True)
        
        response = RedirectResponse(request.session.get("redirect_on_callback", "/noredirect"))   
        request.session["id_token"] = token["id_token"]
        del request.session["redirect_on_callback"]

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
async def logout(request: Request, redirect_on_callback: str):
    request.session["redirect_on_callback"] = redirect_on_callback
    url = settings.SERVER_URL + "/endsession?" + urlencode(
            {
                "id_token_hint": request.session.get("id_token", None),
                "post_logout_redirect_uri": settings.COMPLETE_SERVER_NAME + "/logout_callback"
            },
            
        )
    print(url)
    return RedirectResponse(url)

@router.get("/logout_callback")
async def logout_callback(request: Request):
    response = RedirectResponse(request.session.get("redirect_on_callback", "/noredirect"))        
    del request.session["redirect_on_callback"]
    del request.session["id_token"]

    # issue of response.delete_cookie(key="auth_token") => https://github.com/tiangolo/fastapi/issues/2268
    expires = datetime.datetime.utcnow() + datetime.timedelta(seconds=1)
    response.set_cookie(
            key="auth_token",
            value="",
            expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
            httponly=True,
            samesite='strict',
            domain=settings.SERVER_NAME,
            secure=settings.PRODUCTION_MODE,
        )
    return response
