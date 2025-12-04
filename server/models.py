from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
from datetime import datetime, timezone
from pathlib import Path


#  here we are setting up the database
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DB_PATH = (PROJECT_ROOT / "chat.db").resolve()
engine = create_engine(f"sqlite:///{DB_PATH.as_posix()}", echo=True)
Base = declarative_base()
SessionLocal = sessionmaker(bind=engine)



# Here we are creating the user table
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)



# Here we are creating all the tables
def init_db():
    Base.metadata.create_all(bind=engine)
    print("Database created successfully!")





# Here we are creating the message table
class Message(Base):
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

