from fastapi import FastAPI
from database.connection import create_db_and_tables, check_and_run_seed
from routers import auth, client


app = FastAPI()
app.include_router(auth.router)
app.include_router(client.client_router)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    check_and_run_seed()


@app.get("/")
async def root():
    return {"message": "Hello World" }
