from sqlalchemy import Column, Integer, String, Enum as SQLEnum
from database.database import Base
import enum

class UserRole(enum.Enum):
    user = "user"
    admin = "admin"

class User(Base):
    __tablename__ = "users_realoscan"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    name = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(SQLEnum(UserRole, native_enum=False), default=UserRole.user, nullable=False)
