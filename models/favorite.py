from sqlalchemy import Column, Integer, ForeignKey, String
from database.database import Base  # путь может быть другим, смотри как у тебя

class Favorite(Base):
    __tablename__ = "favorite_realoscan"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users_realoscan.id", ondelete="CASCADE"), nullable=False)
    apartment_id = Column(Integer, ForeignKey("realoscan_data.ID", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), ForeignKey("users_realoscan.email", ondelete="CASCADE"), nullable=False)
