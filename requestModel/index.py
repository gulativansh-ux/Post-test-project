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
    
    
class HiringFacts(BaseModel):
    title: str | None = Field(default=None)
    salary_min: int | None = Field(default=None)
    salary_max: int | None = Field(default=None)
    headcount: int | None = Field(default=None)
    required_skills: list[str] | None = Field(default=None)
    languages: list[str] | None = Field(default=None)
    tech_stacks: list[str] | None = Field(default=None)
    job_tags: list[str] | None = Field(default=None)
    years_of_experience_min: int | None = Field(default=None)
    years_of_experience_max: int | None = Field(default=None)
    jd_text: str | None = Field(default=None)    