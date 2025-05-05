# api/photos.py

import os
from fastapi import APIRouter

router = APIRouter()

PHOTOS_BASE_PATH = "static/media"

@router.get("/get_photos/{apartment_id}")
async def get_photos(apartment_id: int):
    matching_photos = []

    # Ищем папку, где в названии содержится ID
    for folder_name in os.listdir(PHOTOS_BASE_PATH):
        if str(apartment_id) in folder_name:
            folder_path = os.path.join(PHOTOS_BASE_PATH, folder_name)
            if os.path.isdir(folder_path):
                for file_name in os.listdir(folder_path):
                    if file_name.lower().endswith(('.png', '.jpg', '.jpeg', '.webp')):
                        photo_url = f"/{folder_path}/{file_name}".replace("\\", "/")
                        matching_photos.append(photo_url)
            break  # Нашли папку — больше не ищем дальше

    return matching_photos
