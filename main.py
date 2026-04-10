from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException
from sqlmodel import Session, select
from models import Inventory, User, engine, hash_password, verify_password
from pydantic import BaseModel

app = FastAPI()

# Request models
class UserRegister(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: int
    username: str

@app.post("/register", response_model=UserResponse)
async def register(user_data: UserRegister):
    """Register a new user with username and password."""
    with Session(engine) as session:
        # Check if username already exists
        statement = select(User).where(User.username == user_data.username)
        existing_user = session.exec(statement).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Create new user with hashed password
        hashed_pw = hash_password(user_data.password)
        new_user = User(username=user_data.username, hashed_password=hashed_pw)
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return UserResponse(id=new_user.id, username=new_user.username)

@app.post("/login")
async def login(user_data: UserLogin):
    """Login a user by verifying username and password."""
    with Session(engine) as session:
        # Find user by username
        statement = select(User).where(User.username == user_data.username)
        user = session.exec(statement).first()
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Verify password
        if not verify_password(user_data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        return {"message": "Login successful", "user_id": user.id, "username": user.username}


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