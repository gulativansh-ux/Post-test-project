from fastapi import FastAPI
from database.connection import create_db_and_tables, check_and_run_seed


app = FastAPI()

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    check_and_run_seed()


@app.get("/")
async def root():
    return {"message": "Hello World"}
