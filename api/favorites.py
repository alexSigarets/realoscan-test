from fastapi import APIRouter, Depends, HTTPException, Body, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.database import get_db
from models.favorite import Favorite
from models.user import User
from utils.dependencies import get_current_user
from models.apartment import Apartment
from core.limiter import limiter


import os
from dotenv import load_dotenv

load_dotenv()

LIMIT = os.getenv("LIMIT")


router = APIRouter()

@router.post("/favorite")
async def toggle_favorite(
    apartment_id: int = Body(...),
    db: AsyncSession = Depends(get_db),
    user_email: str = Depends(get_current_user)
):
    # Получаем пользователя по email
    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user_id = user.id

    # Проверяем: есть ли уже в избранном?
    exists_result = await db.execute(
        select(Favorite).where(
            Favorite.user_id == user_id,
            Favorite.apartment_id == apartment_id
        )
    )
    exists = exists_result.scalars().first()

    if exists:
        await db.delete(exists)
        await db.commit()
        return {"status": "removed", "message": "Odebráno z oblíbených"}
    else:
        new_fav = Favorite(user_id=user_id, apartment_id=apartment_id, email=user_email)
        db.add(new_fav)
        await db.commit()
        return {"status": "added", "message": "Přidáno k oblíbeným"}





@router.get("/favorite/ids")
async def get_favorite_apartment_ids(
    db: AsyncSession = Depends(get_db),
    user_email: str = Depends(get_current_user)
):
    result = await db.execute(
        select(User).where(User.email == user_email)
    )
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    favs = await db.execute(
        select(Favorite.apartment_id).where(Favorite.user_id == user.id)
    )
    ids = [row[0] for row in favs.all()]
    return ids




@router.get("/favorite/apartments")
@limiter.limit(f"{LIMIT}/minute")  # 👈 не более 10 запросов в минуту с одного IP
async def get_favorite_apartments(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user_email: str = Depends(get_current_user)
):
    # Получаем пользователя
    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Получаем ID всех квартир в избранном
    favs_result = await db.execute(
        select(Favorite.apartment_id).where(Favorite.user_id == user.id)
    )
    apartment_ids = [row[0] for row in favs_result.all()]

    if not apartment_ids:
        return []

    # Получаем сами квартиры
    apartments_result = await db.execute(
        select(Apartment).where(Apartment.ID.in_(apartment_ids))
    )
    apartments = apartments_result.scalars().all()

    return [a.to_dict() for a in apartments]