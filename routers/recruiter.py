from fastapi import APIRouter, Depends
from database.model import User, Role
from database.connection import SessionDep
from sqlmodel import select
from security.jwtUtil import get_current_user


recruiter_router = APIRouter(
    tags=["Recruiter Management"],
    dependencies=[Depends(get_current_user)]
)

@recruiter_router.get("/recruiters")
def list_recruiters(session: SessionDep):
    recruiter_role = session.exec(select(Role).where(Role.name == "recruiter")).first()
    if not recruiter_role:
        return {"message": "Recruiters fetched successfully", "recruiters": []}

    users = session.exec(
        select(User).where(User.role_id == recruiter_role.id)).all()

    recruiter_list = []
    for user in users:
        user_dict = {"id": user.id, "name": user.name, "email": user.email}
        recruiter_list.append(user_dict)

    return {
        "message": "Recruiters fetched successfully",
        "recruiters": recruiter_list
    }