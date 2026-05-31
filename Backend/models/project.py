from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from uuid import UUID

class ProjectBase(BaseModel):
    projectName: str
    projectDescription: Optional[str] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectResponse(ProjectBase):
    projectID: UUID
    userID: UUID
    createdDate: datetime

    class Config:
        from_attributes = True
