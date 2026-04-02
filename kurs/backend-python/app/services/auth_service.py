from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from sqlalchemy.orm import Session
from ..config import get_settings
from ..models.user import User
from ..models.refresh_token import RefreshToken
from ..schemas.auth import Token, TokenData
from ..schemas.user import UserCreate, UserResponse

settings = get_settings()

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.access_token_expire_minutes)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        try:
            payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
            username: str = payload.get("sub")
            if username is None:
                return None
            token_data = TokenData(username=username)
            return token_data
        except JWTError:
            return None
    
    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()
    
    @staticmethod
    def get_user_by_email(db: Session, email: str) -> Optional[User]:
        return db.query(User).filter(User.email == email).first()
    
    @staticmethod
    def create_user(db: Session, user: UserCreate) -> User:
        hashed_password = AuthService.get_password_hash(user.password)
        db_user = User(
            username=user.username,
            email=user.email,
            password=hashed_password
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[User]:
        user = AuthService.get_user_by_username(db, username)
        if not user:
            return None
        if not AuthService.verify_password(password, user.password):
            return None
        return user
    
    @staticmethod
    def create_tokens(user: User) -> Token:
        access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
        refresh_token_expires = timedelta(days=settings.refresh_token_expire_days)
        
        access_token = AuthService.create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        refresh_token = AuthService.create_refresh_token(
            data={"sub": user.username}, expires_delta=refresh_token_expires
        )
        
        return Token(
            access_token=access_token,
            refresh_token=refresh_token,
            token_type="bearer"
        )
    
    @staticmethod
    def store_refresh_token(db: Session, user_id: int, refresh_token: str) -> RefreshToken:
        expires_at = datetime.utcnow() + timedelta(days=settings.refresh_token_expire_days)
        db_refresh_token = RefreshToken(
            user_id=user_id,
            token=refresh_token,
            expires_at=expires_at
        )
        db.add(db_refresh_token)
        db.commit()
        db.refresh(db_refresh_token)
        return db_refresh_token
    
    @staticmethod
    def verify_refresh_token(db: Session, refresh_token: str) -> Optional[User]:
        token_data = AuthService.verify_token(refresh_token)
        if not token_data:
            return None
        
        db_refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            RefreshToken.expires_at > datetime.utcnow()
        ).first()
        
        if not db_refresh_token:
            return None
        
        user = AuthService.get_user_by_username(db, token_data.username)
        return user
    
    @staticmethod
    def revoke_refresh_token(db: Session, refresh_token: str) -> bool:
        db_refresh_token = db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()
        
        if db_refresh_token:
            db.delete(db_refresh_token)
            db.commit()
            return True
        return False
    
    @staticmethod
    def revoke_all_user_tokens(db: Session, user_id: int) -> int:
        deleted_count = db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id
        ).delete()
        db.commit()
        return deleted_count