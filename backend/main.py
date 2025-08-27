from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
import database
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import jobs
import os
import s3_client

app = FastAPI()

from api.v1 import abook as abook_v1

app.include_router(abook_v1.router, prefix="/api/v1")


@app.get("/")
def read_root():
    return {"Hello": "World"}

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/health/db")
def db_health_check(db: Session = Depends(database.get_db)):
    try:
        # to check database connection, we can execute a simple query
        db.execute(text('SELECT 1'))
        return {"status": "ok"}
    except Exception as e:
        return {"status": "error", "detail": str(e)}


scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', days=1)
async def scheduled_cleanup():
    db = database.SessionLocal()
    try:
        jobs.cleanup_inactive_devices(db=db)
    finally:
        db.close()

@app.on_event("startup")
async def startup_event():
    if os.getenv("TESTING") != "1":
        s3_client.create_bucket_if_not_exists()
        scheduler.start()

@app.on_event("shutdown")
async def shutdown_event():
    if os.getenv("TESTING") != "1":
        scheduler.shutdown()
