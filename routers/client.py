from fastapi import APIRouter, HTTPException, Depends, status
from database.model import Client, Role, UserClient
from database.connection import SessionDep
from sqlmodel import select
from security.jwtUtil import get_current_user


client_router = APIRouter(
    tags=["Client Management"]
)

@client_router.get("/clients")
async def fetch_clients(session: SessionDep, userDetail: dict = Depends(get_current_user)):
    clients_data=''
    roleDetail = session.exec(select(Role.name).where(Role.id==userDetail.role_id)).first()
    if roleDetail == "superadmin":
        clients_data =  session.exec(select(Client)).fetchall()
    else:
        allowed_client_id = session.exec(select(UserClient.client_id).where(UserClient.user_id==userDetail.id))
        if not allowed_client_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, 
                detail="You do not have access to any clients."
            )
        clients_data = session.exec(
            select(Client).where(Client.id.in_(allowed_client_id))
        ).all()
    return clients_data