from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Literal
from fastapi import FastAPI

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    userEmail: str | None = None

class JobRequest(BaseModel):
    client_id: int 
    position_title: str
    urgency: Literal["low", "medium", "high"] = "medium"  # Restricts allowed values
    headcount: int | None = None
    salary_min: int | None = None
    salary_max: int | None = None
    search_location: str
    observation: str | None = None
    meeting_transcript: str
    status: Literal["pending", "active", "completed"] = "pending"
    created_by: int
    assigned_to: int  
    extraction_status: str = "idle"


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: str