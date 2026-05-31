from fastapi import APIRouter, HTTPException
from database import supabase
from models.user import UserCreate, UserLogin, UserResponse

router = APIRouter(prefix="/users", tags=["Users"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate):
    # Using Supabase Auth
    try:
        response = supabase.auth.sign_up({
            "email": user.email,
            "password": user.password,
            "options": {
                "data": {
                    "userName": user.userName
                }
            }
        })
        if response.user:
            # Sync to USER table
            db_res = supabase.table("USER").insert({
                "userID": response.user.id,
                "userName": user.userName,
                "email": user.email,
                "password": "hashed_by_supabase_auth" # We don't store actual pw here
            }).execute()
            
            if len(db_res.data) > 0:
                return db_res.data[0]
            
        raise HTTPException(status_code=400, detail="Failed to register user")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/login")
def login(user: UserLogin):
    try:
        response = supabase.auth.sign_in_with_password({
            "email": user.email,
            "password": user.password
        })
        if response.session:
            return {"access_token": response.session.access_token, "user": response.user}
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))
