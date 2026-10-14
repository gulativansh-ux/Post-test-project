from fastapi import APIRouter, HTTPException, Depends
from database.model import Client
from database.connection import SessionDep
from sqlmodel import select
from security.jwtUtil import get_current_user
from database.model import JobRequest
import json



job_request_router = APIRouter(
    tags=["Job Request Management"],
    dependencies=[Depends(get_current_user)] 
)

@job_request_router.post("/job-request")
async def create_job_request(jobRequest: JobRequest , session: SessionDep):
    row = JobRequest (
        client_id= jobRequest.client_id,
        position_title = jobRequest.position_title,
        urgency = jobRequest.urgency,
        headcount = jobRequest.headcount,
        salary_min  = jobRequest.salary_min,
        salary_max  = jobRequest.salary_max,
        search_location = json.dumps(jobRequest.search_location),
        observation = jobRequest.observation,
        meeting_transcript = jobRequest.meeting_transcript,
        status = jobRequest.status,
        created_by = jobRequest.created_by,
        assigned_to = jobRequest.assigned_to,  
        extraction_status = jobRequest.extraction_status,
    )
    session.add(row)
    # print("Before commit row",row)
    # print("Before commit JobRequest",JobRequest)
    session.commit()  
    # print("After commit row",row)
    # print("After commit JobRequest",JobRequest)
    session.refresh(row)
    # print("After Refresh",row)
    return {
        "message": "Data Saved Successfully",
        "data": row
    }
