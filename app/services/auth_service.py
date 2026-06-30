from datetime import datetime, timedelta, timezone

from sqlalchemy.orm import Session
import jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
import os

from app.exceptions import ConflictException
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.database import get_db

password_hash = PasswordHash.recommended()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

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

    # 在這指定演算法使用HS256
    return jwt.encode(payload, os.getenv("SECRET_KEY"), algorithm="HS256")





# User Create
def register(db: Session, data: UserCreate) -> User:
    # 1. Check if user already exists
    user = db.query(User).filter(User.email == data.email).first()
    if user:
        # raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
        raise ConflictException("Email already registered")

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
    # 先直接在DB裡面搜尋是否已有這個用戶存在，如果有存在才需要進一步去進行密碼驗證
    user = db.query(User).filter(User.email == email).first()


    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # verify password，這裡使用pwdlib的verify方法去驗證密碼是否正確，因為我們在註冊時已經將密碼進行hash過了，所以這裡需要將使用者輸入的密碼與資料庫裡的hash密碼進行比對
    if not verify_password(password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")

    # generate JWT Token，這裡使用JWT的sub欄位來存放user id，這樣在之後的驗證中就可以透過sub欄位來取得使用者的id，進而取得使用者的資訊
    # 登入 → 把 user.id 存進 sub → 簽發 token
    # 請求 → 解碼 token → 從 sub 取出 user_id → 查詢 user
    token = create_access_token({"sub": str(user.id)})

    # 指定token type為bearer，其餘的種類還有basic, mac等，這裡使用bearer是因為我們使用JWT token作為認證方式
    return Token(access_token=token, token_type="bearer")


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    try:
        payload = jwt.decode(token, os.getenv('SECRET_KEY'), algorithms=["HS256"])
        user_id = payload.get("sub") # ← 從 sub 取出 user id
        if user_id is None:
            # token 合法，但裡面沒有 sub，不是我們系統發行的
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    except jwt.ExpiredSignatureError:
        # token expired，這是 jwt decode 時會丟出的錯誤，代表 token 已經過期了
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired")

    except jwt.InvalidTokenError:
        # token 本身格式錯誤或簽名被竄改
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    user = db.query(User).filter(User.id == int(user_id)).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user




