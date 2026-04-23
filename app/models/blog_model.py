from sqlalchemy import Column, Integer, String, DateTime,ForeignKey
from app.db.base import Base
from sqlalchemy.sql import func

class Blog(Base):
    __tablename__ = "blogs_tbl"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(String)
    slug = Column(String, unique=True, index=True)
    author_id = Column(Integer, ForeignKey("users_tbl.id"))
    banner_image = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
