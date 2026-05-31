from fastapi import APIRouter, HTTPException
from typing import List
from uuid import UUID
from database import supabase
from models.project import ProjectCreate, ProjectResponse

router = APIRouter(prefix="/projects", tags=["Projects"])

@router.get("/{user_id}", response_model=List[ProjectResponse])
def get_user_projects(user_id: UUID):
    try:
        res = supabase.table("PROJECT").select("*").eq("userID", str(user_id)).execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{user_id}", response_model=ProjectResponse)
def create_project(user_id: UUID, project: ProjectCreate):
    try:
        res = supabase.table("PROJECT").insert({
            "userID": str(user_id),
            "projectName": project.projectName,
            "projectDescription": project.projectDescription
        }).execute()
        if len(res.data) > 0:
            return res.data[0]
        raise HTTPException(status_code=400, detail="Failed to create project")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{project_id}")
def delete_project(project_id: UUID):
    try:
        res = supabase.table("PROJECT").delete().eq("projectID", str(project_id)).execute()
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
