from sqlmodel import SQLModel, Field, create_engine
from typing import Optional

class Inventory(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    category: str
    brand: str
    size: Optional[str] = None
    color: Optional[str] = None
    quantity: int
    price: float

DB_NAME = "warehouse.db"
engine = create_engine(f"sqlite:///{DB_NAME}")
SQLModel.metadata.create_all(engine)
