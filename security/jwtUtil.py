from datetime import datetime, timedelta, timezone
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from fastapi import HTTPException, Depends, status
from typing import Annotated
import jwt
from config import get_settings
from requestModel.index import TokenData
from jwt.exceptions import InvalidTokenError
from database.connection import SessionDep
from database.model import User
from sqlmodel import select


settings = get_settings()
bearer_scheme = HTTPBearer(auto_error=False)


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer_scheme)], session: SessionDep):

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    SECRET_KEY = settings.SECRET_KEY
    ALGORITHM = settings.ALGORITHM
 
    try:
        token_string = token.credentials 
        payload = jwt.decode(token_string, SECRET_KEY, algorithms=[ALGORITHM])
        userEmail = payload.get("sub")
        if userEmail is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        token_data = TokenData(userEmail=userEmail)
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    userDetail = session.exec(select(User).where(User.email==token_data.userEmail.lower())).first()

    if userDetail is None:
       raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return userDetail
