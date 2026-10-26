from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from database.connection import SessionDep
from security.jwtUtil import get_current_user
from sqlmodel import select, desc
from database.model import JobRequest, Role, Jobs, Client, User
from datetime import datetime, timezone
from AI.index import run_ai
from sqlmodel import select, desc

jobs_router = APIRouter(tags=["Jobs Management"])


@jobs_router.get("/check-pending-request")
async def check_pending_request(
    session: SessionDep, userDetail: dict = Depends(get_current_user)
):
    fetch_data = []
    roleDetail = session.exec(
        select(Role.name).where(Role.id == userDetail.role_id)
    ).first()
    if roleDetail == "superadmin":
        fetch_data = session.exec(
            select(JobRequest).where(JobRequest.status == "pending")
            .order_by(desc(JobRequest.id))
        ).all()
    else:
        fetch_data = session.exec(
            select(JobRequest).where(
                JobRequest.status == "pending", JobRequest.assigned_to == userDetail.id
            ).order_by(desc(JobRequest.id))
        ).all()
    return fetch_data


@jobs_router.post("/fullfill-request")
async def fullfill_request(
    request_id: int,
    isAccepted: bool,
    background_task: BackgroundTasks,
    session: SessionDep,
    userDetail: dict = Depends(get_current_user),
):
    job=[]
    status_to_update = "accepted" if isAccepted is True else "rejected"
    row_detail = session.exec(
        select(JobRequest).where(JobRequest.id == request_id)
    ).first()
    if not row_detail:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Current request Id not exist in the table",
        )
    if row_detail.status != "pending":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current request already full-fill.",
        )
    roleDetail = session.exec(
        select(Role.name).where(Role.id == userDetail.role_id)
    ).first()
    
    if roleDetail != "superadmin":
        is_allowed_to_update = row_detail.assigned_to == userDetail.id
        if not is_allowed_to_update:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="You are not allowed to update this record.",
            )
    if status_to_update == "accepted":
        job = Jobs(
            job_request_id=row_detail.id,
            client_id=row_detail.client_id,
            position_title=row_detail.position_title,
            salary_min=row_detail.salary_min,
            salary_max=row_detail.salary_max,
            headcount=row_detail.headcount,
            search_location=row_detail.search_location,
            observation=row_detail.observation,
            urgency=row_detail.urgency,
            status="draft",
            recruiter_id=row_detail.assigned_to,
            extraction_status="processing",
            created_at=datetime.now(timezone.utc),
        )
        row_detail.status = status_to_update
        row_detail.extraction_status = "processing"
        session.add(job)  
        session.commit()
        background_task.add_task(run_ai, job_id=job.id, transcript=row_detail.meeting_transcript, notification_user_id=userDetail.id) 
    else:
        row_detail.status = status_to_update   
    session.add(row_detail)
    session.commit()
    return job

@jobs_router.get("/fetch-jobs")
async def fetch_jobs(
    session: SessionDep, 
    userDetail: dict = Depends(get_current_user)
):
    roleDetail = session.exec(
        select(Role.name).where(Role.id == userDetail.role_id)
    ).first()

    base_query = select(
        Jobs, 
        Client.name.label("client_name"), 
        User.name.label("recruiter_name")
    ).join(
        Client, Jobs.client_id == Client.id
    ).join(
        User, Jobs.recruiter_id == User.id
    ).order_by(desc(Jobs.id))

    if roleDetail == "superadmin":
        result = session.exec(base_query).all()
    else:
        allowed_id = session.exec(
            select(JobRequest.id).where(JobRequest.assigned_to == userDetail.id)
        ).all()
        result = session.exec(
            base_query.where(Jobs.job_request_id.in_(allowed_id))
        ).all()

    fetch_data = []
    for row in result:
        job_data = row.Jobs.model_dump()  
        job_data["client_name"] = row.client_name
        job_data["recruiter_name"] = row.recruiter_name
        fetch_data.append(job_data)

    return fetch_data


@jobs_router.get("/fetch-job-detail")
async def fetch_job_detail(
    requested_job_id: int,
    session: SessionDep,
    userDetail: dict = Depends(get_current_user),
):
    
    statement = (
        select(Jobs, Client.name.label("client_name"))
        .join(Client, Jobs.client_id == Client.id, isouter=True)
        .where(Jobs.id == requested_job_id)
    )
    
    result = session.exec(statement).first() 
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Requested Job Does Not Exist",
        )
        
    job_obj, client_name = result
    
    job_detail_dict = job_obj.model_dump()
    job_detail_dict["client_name"] = client_name

    return job_detail_dict