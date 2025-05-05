from fastapi import FastAPI, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from models.user import User
from database.database import get_db
from utils.password_hashing import verify_password
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from auth.jwt_auth import create_access_token
from dotenv import load_dotenv
import os

from slowapi import Limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")


# Инициализируем лимитер (по IP)
limiter = Limiter(key_func=get_remote_address)


# Импортируем роуты
from api import apartments  # новый импорт!
from api import photos
from api import admin_register
from api import favorites

app = FastAPI()
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)


class UserLogin(BaseModel):
    username: str
    password: str

# Разрешить CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение папки для статики
app.mount("/static", StaticFiles(directory="static"), name="static")

# Подключение папки для шаблонов
templates = Jinja2Templates(directory="templates")

# Регистрируем роуты API
app.include_router(apartments.router, tags=["Apartments"])
app.include_router(photos.router)
app.include_router(admin_register.router)
app.include_router(favorites.router, tags=["favorites"])



# 👉 Маршрут для страницы логина
@app.post("/login/")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    stmt = select(User).where(User.email == user.username)
    result = await db.execute(stmt)
    user_obj = result.scalars().first()

    if not user_obj or not verify_password(user.password, user_obj.hashed_password):
        return JSONResponse(status_code=401, content={"detail": "Nesprávné přihlašovací údaje."})

    token = create_access_token({"sub": user_obj.email, "role": user_obj.role.value})
    return {"token": token, "role": user_obj.role.value}



@app.get("/login/", response_class=HTMLResponse)
async def login_page_redirected(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})



# 👉 Главная страница: проверка токена на стороне клиента
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/favorites", response_class=HTMLResponse)
def get_favorites_page(request: Request):
    return templates.TemplateResponse("favorites.html", {"request": request})

