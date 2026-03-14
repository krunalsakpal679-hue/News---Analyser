from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String
from app.models.base import Base

class TestPlural(Base):
    __tablename__ = "test_plurals"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50))
