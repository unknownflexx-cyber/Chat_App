# models.py

from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime

# -----------------------------
# Database Setup
# -----------------------------
engine = create_engine("sqlite:///chat.db", echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


# -----------------------------
# User Table
# -----------------------------
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)


# -----------------------------
# Message Table
# -----------------------------
class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String(50), nullable=False)
    receiver = Column(String(50), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)


# -----------------------------
# Create all tables
# -----------------------------
def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database created successfully!")


if __name__ == "__main__":
    init_db()
