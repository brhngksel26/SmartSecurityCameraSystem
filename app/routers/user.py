# routers/user.py

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.security import OAuth2PasswordBearer
from fastapi.templating import Jinja2Templates
from fastapi_login import LoginManager
from tortoise.exceptions import IntegrityError

from app.config import config
from app.models.user import User
from app.schemas.user import Token
from app.utils.auth import AuthHandler

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
login_manager = LoginManager(config.SECRET_KEY, token_url="/token")
templates = Jinja2Templates(directory=str(config.TEMPLATES_DIR))
auth_handler = AuthHandler()


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "message": ""})


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    email: str = Form(...),
    password: str = Form(...),
):
    user = User(email=email, password=password)
    if not await auth_handler.authenticate_user(user.email, user.password):
        return templates.TemplateResponse(
            "error.html",
            {
                "request": request,
                "detail": "Incorrect Username or Password",
                "status_code": 404,
            },
        )

    access_token = auth_handler.create_access_token(user.email)

    response = templates.TemplateResponse("private.html", {"request": request})
    response.set_cookie(key="access_token", value=access_token, httponly=True)

    return response


@router.get("/register", response_class=HTMLResponse)
async def register(request: Request):
    return templates.TemplateResponse(
        "register.html", {"request": request, "message": ""}
    )


@router.post("/register", response_class=HTMLResponse)
async def register_user(
    request: Request, email: str = Form(...), password: str = Form(...)
):
    try:
        await User.create(
            email=email, password=auth_handler.get_hash_password(password)
        )
        message = "User registered successfully!"
    except IntegrityError:
        message = "User with this email or username already exists."
        return templates.TemplateResponse(
            "register.html", {"request": request, "message": message}
        )

    except Exception as e:
        message = f"An error occurred: {e}"
        return templates.TemplateResponse(
            "register.html", {"request": request, "message": message}
        )

    return templates.TemplateResponse(
        "login.html", {"request": request, "message": message}
    )
