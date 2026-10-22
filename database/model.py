from sqlmodel import Field, SQLModel
from datetime import datetime


# We use the config table=True to tell SQLModel that this is a table model, it represents a table.
# It's also possible to have models without table=True, those would be only data models, without a table in the database, they would not be table models.


class Client(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    password: str 
    email: str
    role_id: int


class Role(SQLModel, table=True):      
    id: int | None = Field(default=None, primary_key=True)
    name: str


class UserClient(SQLModel, table=True):
    user_id: int | None = Field(default=None, foreign_key="user.id", primary_key=True)
    client_id: int | None = Field(default=None, foreign_key="client.id", primary_key=True)



class JobRequest(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    client_id: int = Field(foreign_key="client.id")
    position_title: str
    urgency: str = "medium"
    headcount: int | None  = None
    salary_min : int | None  = None
    salary_max : int | None  = None
    search_location: str
    observation: str | None = None
    meeting_transcript: str
    status: str = "pending"
    created_by: int = Field(foreign_key="user.id")
    assigned_to: int = Field(foreign_key="user.id")  
    extraction_status: str = "idle"
    
    
class Jobs(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    job_request_id: int = Field(foreign_key="jobrequest.id")
    client_id: int = Field(foreign_key="client.id")
    position_title: str
    salary_min: int | None = None
    salary_max: int | None = None
    headcount: int | None = None
    search_location: str
    required_skills: str | None = None
    languages: str | None = None
    tech_stacks: str | None = None
    job_tags: str | None = None
    years_of_experience_min: int | None = None
    years_of_experience_max: int | None = None
    jd_text: str | None = None
    observation: str | None = None
    urgency: str
    status: str = "draft"
    recruiter_id: int = Field(foreign_key="user.id")
    extraction_status: str = "idle"
    extraction_error: str | None = None
    created_at: datetime
    
