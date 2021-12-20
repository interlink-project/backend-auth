from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from starlette.middleware.cors import CORSMiddleware
from app.api.api_v1.auth import router as authrouter
from app.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,  openapi_url=f"/openapi.json", docs_url="/docs", root_path=settings.BASE_PATH
)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        # allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

app.include_router(authrouter, tags=["auth"])

@app.get("/")
def main():
    return RedirectResponse(url=f"{settings.BASE_PATH}/docs")


@app.get("/healthcheck/")
def healthcheck():
    return True

###################
# we need this to save temporary code & state in session (authentication)
###################

#from app.general.authentication import AuthMiddleware
#app.add_middleware(AuthMiddleware)


from starlette.middleware.sessions import SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)