from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, HTTPException, Depends, Header
from sqlmodel import Session, select
from models import Inventory, User, engine, hash_password, verify_password
from pydantic import BaseModel
import jwt
from datetime import datetime, timedelta
from typing import Optional

app = FastAPI()

# JWT Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 hours

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

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    username: str

# JWT Token Functions
def create_access_token(user_id: int, username: str):
    """Create a JWT access token."""
    payload = {
        "user_id": user_id,
        "username": username,
        "exp": datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES),
        "iat": datetime.utcnow()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token

def verify_token(token: str):
    """Verify JWT token and extract user info."""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        username = payload.get("username")
        if user_id is None or username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return {"user_id": user_id, "username": username}
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def get_current_user(authorization: Optional[str] = Header(None)):
    """Dependency to get current authenticated user."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")
    
    # Extract token from "Bearer <token>"
    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != "bearer":
        raise HTTPException(status_code=401, detail="Invalid authorization format")
    
    token = parts[1]
    return verify_token(token)

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

@app.post("/login", response_model=TokenResponse)
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
        
        # Generate JWT token
        token = create_access_token(user.id, user.username)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user_id=user.id,
            username=user.username
        )


@app.get("/inventory")
async def get_inventory(current_user: dict = Depends(get_current_user)):
    """Get all inventory items (requires authentication)."""
    with Session(engine) as session:
        statement = select(Inventory)
        items = session.exec(statement).all()
        return items

@app.post("/inventory")
async def create_item(item: Inventory, current_user: dict = Depends(get_current_user)):
    """Create a new inventory item (requires authentication)."""
    with Session(engine) as session:
        session.add(item)
        session.commit()
        session.refresh(item)
        return item

@app.delete("/inventory/{id}")
async def delete_item(id: int, current_user: dict = Depends(get_current_user)):
    """Delete an inventory item (requires authentication)."""
    with Session(engine) as session:
        statement = select(Inventory).where(Inventory.id == id)
        record = session.exec(statement).one()
        session.delete(record)
        session.commit()
        return {"deleted": id}

@app.put("/update/{id}")
async def update_item(id: int, item: Inventory, current_user: dict = Depends(get_current_user)):
    """Update an inventory item (requires authentication)."""
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