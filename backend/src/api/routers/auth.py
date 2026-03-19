import logging
from datetime import datetime, timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel

from ...config.settings import Settings

settings = Settings()
from ...database.connection import get_db
from ...database.models import User
from ...database.schemas import UserCreate, UserResponse
from ...services.user_service import UserService

logger = logging.getLogger(__name__)

logger.info("Auth router initialized with prefix /auth")
router = APIRouter(tags=["authentication"])

# Security
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db=Depends(get_db)
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception

    user = UserService.get_by_username(db, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db=Depends(get_db)):
    """Register a new user (for future multi-user support)"""
    # Check if user exists
    existing_user = UserService.get_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # Create user
    user = UserService.create_user(
        db,
        username=user_data.username,
        password=user_data.password
    )
    return user


@router.post("/login", response_model=Token)
def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db=Depends(get_db)
):
    """Authenticate user and return JWT token"""
    logger.info('=' * 60)
    logger.info('[BACKEND] /login endpoint called')
    logger.info(f'[BACKEND] Username received: {form_data.username}')
    logger.info(f'[BACKEND] Password received: {"*" * len(form_data.password) if form_data.password else "(empty)"}')
    
    # For MVP, accept hardcoded credentials
    logger.info('[BACKEND] Checking hardcoded credentials')
    if form_data.username == "user" and form_data.password == "password":
        logger.info('[BACKEND] Hardcoded credentials matched (user/password)')
        # Create access token
        logger.info('[BACKEND] Creating access token')
        access_token = create_access_token(data={"sub": "user"})
        logger.info(f'[BACKEND] Access token created, length: {len(access_token)}')
        logger.info('[BACKEND] Preparing response')
        response = {"access_token": access_token, "token_type": "bearer"}
        logger.info('[BACKEND] Returning success response')
        return response

    logger.info(f'[BACKEND] Hardcoded credentials did NOT match. Checking database for user: {form_data.username}')
    # Check database for user (for future multi-user support)
    logger.info('[BACKEND] Querying database for user')
    user = UserService.get_by_username(db, form_data.username)
    if not user:
        logger.warning(f'[BACKEND] User NOT found in database: {form_data.username}')
        logger.info('[BACKEND] Raising HTTPException for invalid credentials')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f'[BACKEND] User found in database: id={user.id}, username={user.username}')
    logger.info(f'[BACKEND] Verifying password for user {form_data.username}')
    if not verify_password(form_data.password, user.hashed_password):
        logger.warning(f'[BACKEND] Password verification FAILED for user: {form_data.username}')
        logger.info('[BACKEND] Raising HTTPException for invalid password')
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    logger.info(f'[BACKEND] Password verified successfully for user: {form_data.username}')
    access_token = create_access_token(data={"sub": user.username})
    logger.info(f'[BACKEND] Access token created, length: {len(access_token)}')
    logger.info('[BACKEND] Returning success response')
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    """Get current user information"""
    return current_user


def create_access_token(data: dict):
    """Create JWT access token"""
    logger.info(f'[BACKEND] Creating access token with data: {data}')
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    logger.info(f'[BACKEND] Token will expire at: {expire}')
    logger.info(f'[BACKEND] Encoding JWT with algorithm: {settings.ALGORITHM}')
    encoded_jwt = jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    logger.info(f'[BACKEND] JWT encoded successfully')
    return encoded_jwt