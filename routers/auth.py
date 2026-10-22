from fastapi import APIRouter, HTTPException
from requestModel.index import UserLogin
from database.model import User, Role
from database.connection import SessionDep
from sqlmodel import select
from security.passwordUtils import checkPassword
from security.jwtUtil import create_access_token
from config import get_settings
from datetime import timedelta
from requestModel.index import UserResponse


router = APIRouter()
settings = get_settings()

def user_to_response(user: User, session: SessionDep):
    role = session.get(Role, user.role_id)
    return UserResponse(
        id=user.id,
        name=user.name,
        email=user.email,
        role=role.name if role else "",
    )

@router.post("/auth",tags=["Authentication User"])
async def read_user_me(userDetail: UserLogin, session: SessionDep):
    userExist =  session.exec(select(User).where(User.email==userDetail.email.lower())).first()
    if not userExist:
        raise HTTPException(status_code=404, detail="User not found")
    validPassword = checkPassword(userDetail.password , userExist.password)
    if not validPassword:
        raise HTTPException(status_code=401, detail="Unauthorized")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token (
        data={"sub": userExist.email}, expires_delta=access_token_expires
    )
    return { "access_token" : access_token, "token_type" : "bearer", "user": user_to_response(userExist, session),  }
