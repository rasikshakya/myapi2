import os
from datetime import date, datetime, timezone
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from supabase import create_client, Client

app = FastAPI(title="F1 Driver API")

# --- CORS SETTINGS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://zhangsgithub04.github.io",
        "https://rasikshakya.github.io" # Added your origin
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- SUPABASE CONFIG ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MY_API_KEY = os.getenv("MY_API_KEY") # Secret key for POST/PATCH/DELETE

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Missing Supabase credentials in environment variables")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- SECURITY CHECK ---
def verify_token(authorization: Optional[str] = Header(None)):
    if authorization is None:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer" or token != MY_API_KEY:
            raise HTTPException(status_code=403, detail="Invalid or unauthorized token")
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization format")

# --- DATA MODELS ---
class DriverCreate(BaseModel):
    driver_name: str = Field(..., min_length=1)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    country_of_origin: str = Field(..., min_length=1)
    birthdate: date

class DriverUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country_of_origin: Optional[str] = None
    birthdate: Optional[date] = None

# --- ROUTES ---

@app.get("/")
async def root():
    response = supabase.table("f1_drivers").select("*", count="exact").execute()
    return {
        "message": "F1 Driver API is running",
        "driver_count": response.count
    }

@app.get("/drivers")
async def list_drivers():
    response = supabase.table("f1_drivers").select("*").order("driver_name").execute()
    return response.data

@app.get("/drivers/{driver_name}")
async def get_driver(driver_name: str):
    response = supabase.table("f1_drivers").select("*").eq("driver_name", driver_name).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Driver not found")
    return response.data[0]

@app.post("/drivers", status_code=201, dependencies=[Depends(verify_token)])
async def create_driver(driver: DriverCreate):
    payload = driver.model_dump()
    # Convert date to string for Supabase
    payload["birthdate"] = payload["birthdate"].isoformat()
    
    response = supabase.table("f1_drivers").insert(payload).execute()
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create driver")
    return response.data[0]

@app.patch("/drivers/{driver_name}", dependencies=[Depends(verify_token)])
async def update_driver(driver_name: str, driver: DriverUpdate):
    update_data = driver.model_dump(exclude_none=True)
    
    if "birthdate" in update_data:
        update_data["birthdate"] = update_data["birthdate"].isoformat()

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    response = supabase.table("f1_drivers").update(update_data).eq("driver_name", driver_name).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Driver not found")
    return response.data[0]

@app.delete("/drivers/{driver_name}", dependencies=[Depends(verify_token)])
async def delete_driver(driver_name: str):
    response = supabase.table("f1_drivers").delete().eq("driver_name", driver_name).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Driver not found")
    return {"message": f"Driver {driver_name} deleted successfully"}
