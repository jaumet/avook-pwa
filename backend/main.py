from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from sqlalchemy import text
import database
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import jobs
import os
import s3_client
import models
import auth

limiter = Limiter(key_func=get_remote_address)
scheduler = AsyncIOScheduler()

def create_initial_admin_user():
    db = database.SessionLocal()
    try:
        print("--- Checking for initial admin user ---")
        user_count = db.query(models.AdminUser).count()
        print(f"--- Found {user_count} existing admin users ---")

        if user_count == 0:
            print("--- No admin users found, attempting to create one. ---")
            email = os.getenv("ADMIN_EMAIL")
            password = os.getenv("ADMIN_PASSWORD")

            print(f"--- Read ADMIN_EMAIL from env: {'present' if email else 'NOT PRESENT'}")
            print(f"--- Read ADMIN_PASSWORD from env: {'present' if password else 'NOT PRESENT'}")

            if email and password:
                hashed_password = auth.get_password_hash(password)
                initial_user = models.AdminUser(
                    email=email,
                    password_hash=hashed_password,
                    role=models.RoleEnum.owner
                )
                db.add(initial_user)
                db.commit()
                print(f"--- Initial admin user '{email}' created successfully. ---")
            else:
                print("--- ADMIN_EMAIL or ADMIN_PASSWORD not set. Skipping initial user creation. ---")
    finally:
        db.close()

@scheduler.scheduled_job('interval', days=1)
async def scheduled_cleanup():
    db = database.SessionLocal()
    try:
        jobs.cleanup_inactive_devices(db=db)
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    print("--- Running application startup logic ---")
    if os.getenv("TESTING") != "1":
        create_initial_admin_user()
        s3_client.create_bucket_if_not_exists()
        # scheduler.start() # Temporarily disabled for debugging
        print("--- Job scheduler is temporarily disabled for debugging ---")
    yield
    # Shutdown logic
    print("--- Running application shutdown logic ---")
    if os.getenv("TESTING") != "1" and scheduler.running:
        scheduler.shutdown()

app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)


# Allow cross-origin requests during development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from api.v1 import abook as abook_v1
from api.v1 import admin_auth as admin_auth_v1
from api.v1 import admin as admin_v1

app.include_router(abook_v1.router, prefix="/api/v1")
app.include_router(admin_auth_v1.router, prefix="/api/v1")
app.include_router(admin_v1.router, prefix="/api/v1")
print("Admin routers included successfully.")


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
