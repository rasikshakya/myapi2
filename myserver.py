import os
from fastapi import FastAPI, Header, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
from supabase import create_client, Client # Ensure this is in your requirements.txt

app = FastAPI()

# --- DATABASE CONNECTION ---
# These must match your Render Environment Variable names exactly
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- SECURITY CONFIG ---
# This must match the 'Key' column in your Render settings
API_KEY_NAME = "YOUR_SUPER_SECRET_KEY"
ACTUAL_API_KEY = os.getenv(API_KEY_NAME)

# --- DATA BLUEPRINTS (Pydantic Models) ---
# This is what was missing and causing the 500 error!
class DriverCreate(BaseModel):
    driver_name: str
    first_name: str
    last_name: str
    country_of_origin: str
    birthdate: str

class DriverUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country_of_origin: Optional[str] = None
    birthdate: Optional[str] = None

# --- AUTHENTICATION LOGIC ---
def verify_api_key(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    
    expected_format = f"Bearer {ACTUAL_API_KEY}"
    if authorization != expected_format:
        raise HTTPException(status_code=401, detail="Invalid Authorization Token")
    
    return authorization

# --- ROUTES ---

@app.get("/drivers")
async def get_drivers():
    response = supabase.table("f1_drivers").select("*").execute()
    return response.data

@app.post("/drivers", status_code=201)
async def create_driver(driver: DriverCreate, auth: str = Depends(verify_api_key)):
    # This line sends the data to your actual database
    response = supabase.table("f1_drivers").insert(driver.dict()).execute()
    return {"message": f"Driver {driver.driver_name} added to the grid!"}

@app.patch("/drivers/{driver_name}")
async def update_driver(driver_name: str, updates: DriverUpdate, auth: str = Depends(verify_api_key)):
    response = supabase.table("f1_drivers").update(updates.dict(exclude_unset=True)).eq("driver_name", driver_name).execute()
    return {"message": f"Updated details for {driver_name}"}

@app.delete("/drivers/{driver_name}")
async def delete_driver(driver_name: str, auth: str = Depends(verify_api_key)):
    response = supabase.table("f1_drivers").delete().eq("driver_name", driver_name).execute()
    return {"message": f"Driver {driver_name} removed from the registry"}
