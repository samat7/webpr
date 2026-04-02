from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.user import UserCreate, UserResponse, UserLogin
from ..schemas.auth import Token, RefreshTokenRequest
from ..services.auth_service import AuthService
from ..dependencies import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    if AuthService.get_user_by_username(db, user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    if AuthService.get_user_by_email(db, user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user
    db_user = AuthService.create_user(db, user)
    
    # Create tokens
    tokens = AuthService.create_tokens(db_user)
    
    # Store refresh token
    AuthService.store_refresh_token(db, db_user.id, tokens.refresh_token)
    
    return tokens

@router.post("/login", response_model=Token)
async def login(user_credentials: UserLogin, db: Session = Depends(get_db)):
    user = AuthService.authenticate_user(db, user_credentials.username, user_credentials.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    tokens = AuthService.create_tokens(user)
    
    # Store refresh token
    AuthService.store_refresh_token(db, user.id, tokens.refresh_token)
    
    return tokens

@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_request: RefreshTokenRequest, db: Session = Depends(get_db)):
    user = AuthService.verify_refresh_token(db, refresh_request.refresh_token)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Revoke old refresh token
    AuthService.revoke_refresh_token(db, refresh_request.refresh_token)
    
    # Create new tokens
    tokens = AuthService.create_tokens(user)
    
    # Store new refresh token
    AuthService.store_refresh_token(db, user.id, tokens.refresh_token)
    
    return tokens

@router.post("/logout")
async def logout(
    refresh_request: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    AuthService.revoke_refresh_token(db, refresh_request.refresh_token)
    return {"message": "Successfully logged out"}

@router.post("/logout-all")
async def logout_all(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    deleted_count = AuthService.revoke_all_user_tokens(db, current_user.id)
    return {"message": f"Logged out from {deleted_count} devices"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user