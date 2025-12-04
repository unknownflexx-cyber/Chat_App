"""
Database models and setup for the chat application.

This module defines:
- The SQLite database connection.
- SQLAlchemy ORM models for User and Message.
- The init_db() function that creates tables at startup.
"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
from pathlib import Path


# Here we are setting up the database
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = (PROJECT_ROOT / "chat.db").resolve()
engine = create_engine(f"sqlite:///{DB_PATH.as_posix()}", echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)


class User(Base):
    """
    ORM model for the 'users' table.

    Stores:
    - Unique username
    - Hashed password
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)


def init_db():
    """
    Here we are creating all database tables if they do not already exist.
    """
    Base.metadata.create_all(bind=engine)
    print("Database created successfully!")


class Message(Base):
    """
    Here we are defining the ORM model for the 'messages' table.

    Stores:
    - Auto-increment message ID
    - Sender username
    - Receiver (always 'ALL' for global chat)
    - Message text
    - Timestamp in UTC
    """
    __tablename__ = "messages"
    __table_args__ = {'sqlite_autoincrement': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    sender = Column(String(50), nullable=False)
    receiver = Column(String(50), nullable=False)
    text = Column(Text, nullable=False)
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)) 


    # Here we are initializing the database
if __name__ == "__main__":
    init_db()

