from fastapi import APIRouter, HTTPException
from typing import List
from database import supabase
from models.standard import MotorResponse, ChainResponse, MaterialResponse

router = APIRouter(prefix="/standards", tags=["Standards"])

@router.get("/motors", response_model=List[MotorResponse])
def get_motors():
    try:
        res = supabase.table("STD_MOTOR").select("*").execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/chains", response_model=List[ChainResponse])
def get_chains():
    try:
        res = supabase.table("STD_CHAIN").select("*").execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/materials", response_model=List[MaterialResponse])
def get_materials():
    try:
        res = supabase.table("STD_MATERIAL").select("*").execute()
        return res.data
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
