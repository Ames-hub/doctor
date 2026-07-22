from sqlalchemy.orm import sessionmaker, declarative_base, Session
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///./database.db"

# Engine
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Needed for SQLite only
)
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)
Base = declarative_base()

def get_db() -> Session:
    return SessionLocal()

# Create all tables
def create_tables():
    """
    Creates all tables registered with Base.
    
    Import your models before calling this,
    otherwise SQLAlchemy won't know they exist.
    """

    Base.metadata.create_all(bind=engine)