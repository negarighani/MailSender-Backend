from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy import Column, DateTime, func

user_category_association = Table(
    "user_category_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("category_id", Integer, ForeignKey("categories.id")),
)

letter_category_association = Table(
    "letter_category_association",
    Base.metadata,
    Column("letter_id", Integer, ForeignKey("letters.id")),
    Column("category_id", Integer, ForeignKey("categories.id")),
)

user_letter_association = Table(
    "user_letter_association",
    Base.metadata,
    Column("user_id", Integer, ForeignKey("users.id")),
    Column("letter_id", Integer, ForeignKey("letters.id")),
)

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)

    categories = relationship("Category", secondary=user_category_association, back_populates="users")
    letters = relationship("Letter", secondary=user_letter_association, back_populates="users")

class Letter(Base):
    __tablename__ = "letters"

    id = Column(Integer, primary_key=True, index=True)
    subject = Column(String)
    content = Column(String)
    created_time = Column(DateTime, default=func.now())

    categories = relationship("Category", secondary=letter_category_association, back_populates="letters")
    users = relationship("User", secondary=user_letter_association, back_populates="letters")

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True)

    users = relationship("User", secondary=user_category_association, back_populates="categories")
    letters = relationship("Letter", secondary=letter_category_association, back_populates="categories")
