import os
from fastapi import FastAPI, Header, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from typing import Optional
from pydantic import BaseModel
from supabase import create_client, Client
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"], 
)

# --- SECURITY CONFIG ---
API_KEY_NAME = "YOUR_SUPER_SECRET_KEY"
ACTUAL_API_KEY = os.getenv(API_KEY_NAME)
security = HTTPBearer()

# --- DATABASE CONNECTION ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- DATA MODELS ---
class DriverCreate(BaseModel):
    driver_name: str
    first_name: str
    last_name: str
    country_of_origin: str
    birthdate: str

# Model for PATCH (all fields are optional)
class DriverUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    country_of_origin: Optional[str] = None
    birthdate: Optional[str] = None

# --- AUTH LOGIC ---
def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security)):
    if credentials.credentials != ACTUAL_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid Authorization Token")
    return credentials.credentials

# --- ROUTES ---

@app.get("/drivers")
async def get_drivers():
    response = supabase.table("f1_drivers").select("*").execute()
    return response.data

@app.post("/drivers", status_code=201)
async def create_driver(driver: DriverCreate, token: str = Depends(verify_api_key)):
    response = supabase.table("f1_drivers").insert(driver.dict()).execute()
    return {"message": f"Driver {driver.driver_name} added!"}

# PUT: Full Replacement
@app.put("/drivers/{driver_name}")
async def replace_driver(driver_name: str, driver: DriverCreate, token: str = Depends(verify_api_key)):
    response = supabase.table("f1_drivers").update(driver.dict()).eq("driver_name", driver_name).execute()
    return {"message": f"Driver {driver_name} fully replaced", "data": response.data}

# PATCH: Partial Update (The route you were looking for!)
@app.patch("/drivers/{driver_name}")
async def update_driver(driver_name: str, updates: DriverUpdate, token: str = Depends(verify_api_key)):
    # exclude_unset=True ensures we only send fields the user actually provided
    data_to_update = updates.dict(exclude_unset=True)
    if not data_to_update:
        raise HTTPException(status_code=400, detail="No fields provided for update")
        
    response = supabase.table("f1_drivers").update(data_to_update).eq("driver_name", driver_name).execute()
    return {"message": f"Driver {driver_name} partially updated", "data": response.data}

@app.delete("/drivers/{driver_name}")
async def delete_driver(driver_name: str, token: str = Depends(verify_api_key)):
    response = supabase.table("f1_drivers").delete().eq("driver_name", driver_name).execute()
    return {"message": f"Driver {driver_name} removed"}
