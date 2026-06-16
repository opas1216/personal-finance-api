from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
import jwt
from fastapi import HTTPException, status
from pwdlib import PasswordHash
import os
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token

password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """
    Hash the password using bcrypt algorithm.
    """
    return password_hash.hash(password)



def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify the password against the hashed password.
    """
    return password_hash.verify(plain_password, hashed_password)


def create_access_token(data: dict) -> str:
    """
    Create a JWT access token.
    """
    payload = data.copy()
    payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=1)
    return jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")





# User Create
def register(db: Session, data: UserCreate) -> User:
    # 1. Check if user already exists
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # 2. Hash the password
    hashed_password = hash_password(data.password)


    # 3. Create user model instance
    user = User(email=data.email,
                password_hash=hashed_password,)


    # 4. Save to database
    db.add(user)
    db.commit()
    db.refresh(user)

    return user

def login(db: Session, email: str, password: str) -> Token:
    user = db.query(User).filter(User.email == email).first()

    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")

    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")

    token = create_access_token({"sub": str(user.id)})

    return Token(access_token=token, token_type="bearer")

