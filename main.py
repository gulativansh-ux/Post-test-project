from fastapi import FastAPI
from database.connection import create_db_and_tables, check_and_run_seed
from routers import auth, client, job_request, recruiter  
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.include_router(auth.router)
app.include_router(client.client_router)
app.include_router(job_request.job_request_router)
app.include_router(recruiter.recruiter_router)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    check_and_run_seed()


@app.get("/")
async def root():
    return {"message": "Hello World" }
