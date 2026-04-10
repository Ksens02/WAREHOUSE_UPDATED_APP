from sqlmodel import SQLModel, Field, create_engine
from typing import Optional
import bcrypt

class Inventory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str
    brand: str
    size: Optional[str] = None
    color: Optional[str] = None
    quantity: int
    price: float

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str

DB_NAME = "warehouse.db"
engine = create_engine(f"sqlite:///{DB_NAME}")
SQLModel.metadata.create_all(engine)

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')

def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    return bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8'))
