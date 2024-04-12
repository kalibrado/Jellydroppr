"""
# --------------------------------------------------------------------------
# App Jellydroppr
# --------------------------------------------------------------------------
"""

from typing import Dict

from fastapi import Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates

from rich.console import Console


from modules.settings import Settings
from modules.oauth import OAuth
from modules.database import DataBase
from modules.forms import LoginForm


console = Console()

app = FastAPI(
    title="Jellydroppr API",
    docs_url="/v1/documentation",
    version="1.0.0",
)
templates = Jinja2Templates(directory="templates")


settings = Settings()
database = DataBase()


oatuh = OAuth(tokenUrl="token", settings=settings, database=database)


@app.post("token")
def login_for_access_token(
    response: Response, form_data: OAuth2PasswordRequestForm = Depends()
) -> Dict[str, str]:
    user = oatuh.authenticate_user(form_data.username, form_data.password)
    if user:
        access_token = oatuh.create_access_token(data=user, settings=settings)
        # Set an HttpOnly cookie in the response. `httponly=True` prevents
        # JavaScript from reading the cookie.
        response.set_cookie(
            key=settings.COOKIE_NAME, value=f"Bearer {access_token}", httponly=True
        )
        return {settings.COOKIE_NAME: access_token, "token_type": "bearer"}

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect email or password",
    )


# --------------------------------------------------------------------------
# Home Page
# --------------------------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    try:
        user = oatuh.get_current_user_from_cookie(request)
        return templates.TemplateResponse(
            "index.html",
            {
                "user": user,
                "request": request,
            },
        )
    except HTTPException as e:
        print("Exception:", e)
        return templates.TemplateResponse(
            "login.html",
            {
                "user": None,
                "request": request,
            },
        )


# --------------------------------------------------------------------------
# Settings Page
# --------------------------------------------------------------------------
@app.get("/settings", response_class=HTMLResponse)
def page_settings(request: Request):
    try:
        user = oatuh.get_current_user_from_cookie(request)
        return templates.TemplateResponse(
            "settings.html",
            {
                "user": user,
                "request": request,
            },
        )
    except HTTPException as e:
        print("Exception:", e)
        return templates.TemplateResponse(
            "login.html",
            {
                "user": None,
                "request": request,
            },
        )


# --------------------------------------------------------------------------
# Login - GET
# --------------------------------------------------------------------------
@app.get("/auth/login", response_class=HTMLResponse)
def login_get(request: Request):
    context = {
        "request": request,
    }
    return templates.TemplateResponse("login.html", context)


@app.post("/auth/login", response_class=HTMLResponse)
async def login_post(request: Request):
    form = LoginForm(request)
    await form.load_data()
    if await form.is_valid():
        try:
            response = RedirectResponse("/", status.HTTP_302_FOUND)
            login_for_access_token(response=response, form_data=form)
            form.__dict__.update(msg="Login Successful!")
            console.log("[green]Login successful!!!!")
            return response
        except HTTPException:
            form.__dict__.update(msg="")
            form.__dict__.get("errors").append("Incorrect Email or Password")
            return templates.TemplateResponse("login.html", form.__dict__)
    return templates.TemplateResponse("login.html", form.__dict__)


# --------------------------------------------------------------------------
# Logout
# --------------------------------------------------------------------------
@app.get("/auth/logout", response_class=HTMLResponse)
def logout_get():
    response = RedirectResponse(url="/")
    response.delete_cookie(settings.COOKIE_NAME)
    return response


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9999)
