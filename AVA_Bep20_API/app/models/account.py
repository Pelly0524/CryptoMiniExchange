from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.models.base import Base


class Account(Base):
    __tablename__ = "account"

    AccountID = Column(String, primary_key=True, autoincrement=True)
    Password = Column(String, nullable=False)
    Name = Column(String, nullable=False)
    Phone = Column(String, nullable=True)
    CreateTime = Column(DateTime, nullable=False)
    IsEmailVerify = Column(Boolean, default=False)
