from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from database.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from utils.dependencies import require_admin
from fastapi.templating import Jinja2Templates
from models.user import User
from sqlalchemy import select

router = APIRouter()
templates = Jinja2Templates(directory="templates")

@router.get("/admin/register", response_class=HTMLResponse)
async def show_registration_form(request: Request, user=Depends(require_admin)):
    return templates.TemplateResponse("admin_register.html", {"request": request})

@router.post("/admin/register")
async def register_user(
    email: str = Form(...),
    name: str = Form(...),
    password: str = Form(...),
    role: str = Form(...),
    db: AsyncSession = Depends(get_db)
):
    from models.user import User, UserRole
    from utils.password_hashing import hash_password

    # ✅ ДОБАВЬ ВОТ ЭТУ ПРОВЕРКУ ПЕРЕД СОЗДАНИЕМ ПОЛЬЗОВАТЕЛЯ
    existing = await db.execute(select(User).where(User.email == email))
    if existing.scalars().first():
        return JSONResponse(status_code=400, content={"detail": "Email již existuje"})

    # 💡 Переименуем переменную user → new_user (чтобы не конфликтовала с Depends выше)
    new_user = User(
        email=email,
        name=name,
        hashed_password=hash_password(password),
        role=UserRole(role)
    )
    db.add(new_user)
    await db.commit()
    return RedirectResponse("/admin/register", status_code=303)



#Получение пользователей (для админа):
@router.get("/admin/users")
async def get_users(db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    result = await db.execute(select(User))
    users = result.scalars().all()
    return [{"id": u.id, "email": u.email, "name": u.name, "role": u.role.value} for u in users]



# Удаление пользователей (для админа):
@router.delete("/admin/users/{user_id}")
async def delete_user(user_id: int, db: AsyncSession = Depends(get_db), user=Depends(require_admin)):
    result = await db.execute(select(User).where(User.id == user_id))
    user_obj = result.scalars().first()
    if not user_obj:
        return JSONResponse(status_code=404, content={"detail": "Uživatel nenalezen"})

    await db.delete(user_obj)
    await db.commit()
    return {"success": True}
