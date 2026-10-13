from fastapi import APIRouter, HTTPException, Depends
from database.model import Client
from database.connection import SessionDep
from sqlmodel import select
from security.jwtUtil import get_current_user


client_router = APIRouter(
    tags=["Client Management"],
    dependencies=[Depends(get_current_user)] 
)

@client_router.post("/client")
async def fetch_clients(session: SessionDep):
    clients_data =  session.exec(select(Client)).fetchall()
    if not clients_data:
        raise HTTPException(status_code=404, detail="Client not found")
    return clients_data