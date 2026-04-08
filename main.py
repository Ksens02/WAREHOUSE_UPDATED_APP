from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI 
from sqlmodel import Session, select
from models import Inventory, engine

app = FastAPI()

@app.get("/inventory")
async def get_inventory():
    with Session(engine) as session:
        statement = select(Inventory)
        items = session.exec(statement).all()
        return items

@app.post("/inventory")
async def create_item(item: Inventory):
    with Session(engine) as session:
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

@app.delete("/inventory/{id}")
async def delete_item(id: int):
    with Session(engine) as session:
        statement = select(Inventory).where(Inventory.id == id)
        record = session.exec(statement).one()
        session.delete(record)
        session.commit()
        return {"deleted": id}

@app.put("/update/{id}")
async def update_item(id: int, item: Inventory):
    with Session(engine) as session:
        statement = select(Inventory).where(Inventory.id == id)
        record = session.exec(statement).one()
        record.name = item.name
        record.category = item.category
        record.brand = item.brand
        record.size = item.size
        record.color = item.color
        record.quantity = item.quantity
        record.price = item.price
        session.add(record)
        session.commit()
        session.refresh(record)
        return record

app.mount("/", StaticFiles(directory="static", html=True), name="static")