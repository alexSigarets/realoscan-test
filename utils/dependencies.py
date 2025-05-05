from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from models.user import UserRole
import os

SECRET_KEY = os.getenv("SECRET_KEY", "supersecretkey")
ALGORITHM = os.getenv("ALGORITHM", "HS256")

security = HTTPBearer(auto_error=False)

async def require_admin(request: Request, creds: HTTPAuthorizationCredentials = Depends(security)):
    token = None

    if creds:
        token = creds.credentials
    elif "token" in request.cookies:
        token = request.cookies["token"]

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        role = payload.get("role")
        if role != UserRole.admin.value:
            raise HTTPException(status_code=403, detail="Only admins allowed")
        return payload  # Можно использовать дальше, если нужно
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
    


async def get_current_user(request: Request, creds: HTTPAuthorizationCredentials = Depends(security)) -> str:
    token = None

    if creds:
        token = creds.credentials
    elif "token" in request.cookies:
        token = request.cookies["token"]

    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if not user_email:
            raise HTTPException(status_code=401, detail="Invalid token payload: missing email")
        return user_email  # ← теперь возвращается email
    except JWTError:
        raise HTTPException(status_code=403, detail="Invalid token")
