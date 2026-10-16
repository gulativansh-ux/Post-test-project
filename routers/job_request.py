from fastapi import APIRouter, Depends
from database.connection import SessionDep
from sqlmodel import select
from security.jwtUtil import get_current_user
from database.model import JobRequest, User
import json
from database.model import Role, Client, UserClient

job_request_router = APIRouter(tags=["Job Request Management"])


@job_request_router.post("/job-requests")
async def create_job_request(
    jobRequest: JobRequest,
    session: SessionDep,
    userDetail: dict = Depends(get_current_user),
):
    assigned_to_name = ""
    assigned_to_id= jobRequest.assigned_to or userDetail.id
    row = ""
    roleDetail = session.exec(
        select(Role.name).where(Role.id == userDetail.role_id)
    ).first()
    if roleDetail == "superadmin":
        allowed_client = session.exec(
            select(UserClient.client_id).where(
                UserClient.user_id == jobRequest.assigned_to
            )
        ).all()
        if jobRequest.client_id not in allowed_client:
            newData = UserClient(
                user_id=jobRequest.assigned_to, client_id=jobRequest.client_id
            )
            session.add(newData)
            session.commit()         
    row = JobRequest(
        client_id=jobRequest.client_id,
        position_title=jobRequest.position_title,
        urgency=jobRequest.urgency,
        headcount=jobRequest.headcount,
        salary_min=jobRequest.salary_min,
        salary_max=jobRequest.salary_max,
        search_location=json.dumps(jobRequest.search_location),
        observation=jobRequest.observation,
        meeting_transcript=jobRequest.meeting_transcript,
        status=jobRequest.status,
        created_by=userDetail.id,
        assigned_to=assigned_to_id,
        extraction_status=jobRequest.extraction_status,
    )
    session.add(row)
    # print("Before commit row",row)
    # print("Before commit JobRequest",JobRequest)
    session.commit()
    # print("After commit row",row)
    # print("After commit JobRequest",JobRequest)
    session.refresh(row)
    # print("After Refresh",row)
    assigned_to_name = session.exec(
        select(User.name).where(User.id == assigned_to_id)
    ).first()
    return {
        "message": "Data Saved Successfully",
        "job_request_data": row,
        "assigned_to_name": assigned_to_name,
    }
