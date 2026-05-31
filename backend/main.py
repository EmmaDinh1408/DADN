from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import users, projects, standards, ai_engine

app = FastAPI(
    title="MechDrive Studio API",
    description="Backend API with AI Engine for MechDrive Studio",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, allow all. Change in prod.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(standards.router)
app.include_router(ai_engine.router)

@app.get("/")
def root():
    return {"message": "Welcome to MechDrive Studio API"}
