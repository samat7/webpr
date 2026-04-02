from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine
from .models import Base
from .routers import auth_router, tasks_router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Todo List API",
    description="A full-stack Todo List application with JWT authentication",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(tasks_router)

@app.get("/health")
async def health_check():
    return {"status": "OK", "message": "Todo List API is running"}

@app.get("/")
async def root():
    return {"message": "Welcome to Todo List API"}