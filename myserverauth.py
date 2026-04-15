import os
from datetime import date, datetime, timezone
from typing import Optional, List

from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from supabase import create_client, Client

app = FastAPI(
    title="F1 Driver API",
    docs_url="/docs",    
    redoc_url="/redoc",  
    openapi_url="/openapi.json" 
)

# --- CORS SETTINGS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:5500",
        "http://localhost:5500",
        "https://zhangsgithub04.github.io",
        "https://rasikshakya.github.io"
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ENVIRONMENT VARIABLES ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
MY_API_KEY = os.getenv("MY_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, MY_API_KEY]):
    raise RuntimeError("Missing SUPABASE_URL, SUPABASE_KEY, or MY_API_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- UTILS & AUTH ---
def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()

def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    """Verifies that the X-API-Key header matches the environment variable."""
    if x_api_key != MY_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key",
        )
    return x_api_key

# --- SCHEMAS ---
class DriverCreate(BaseModel):
    driver_name: str = Field(..., min_length=1)
    first_name: str = Field(..., min_length=1)
    last_name: str = Field(..., min_length=1)
    country_of_origin: str = Field(..., min_length=1)
    birthdate: date

class DriverUpdate(BaseModel):
    first_name: Optional[str] = Field(None, min_length=1)
    last_name: Optional[str] = Field(None, min_length=1)
    country_of_origin: Optional[str] = Field(None, min_length=1)
    birthdate: Optional[date] = None

# --- ROUTES ---

@app.get("/")
async def root():
    response = supabase.table("f1_drivers").select("*", count="exact").execute()
    return {
        "message": "F1 Driver API (Header Auth) is running",
        "driver_count": response.count,
    }

@app.get("/drivers")
async def list_drivers(api_key: str = Depends(require_api_key)):
    response = supabase.table("f1_drivers").select("*").order("driver_name").execute()
    return response.data

@app.get("/drivers/{driver_name}")
async def get_driver(driver_name: str, api_key: str = Depends(require_api_key)):
    response = supabase.table("f1_drivers").select("*").eq("driver_name", driver_name).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Driver not found")
    return response.data[0]

@app.post("/drivers", status_code=201)
async def create_driver(driver: DriverCreate, api_key: str = Depends(require_api_key)):
    payload = driver.model_dump()
    payload["birthdate"] = payload["birthdate"].isoformat()
    # Note: Added 'updated_at' if your table supports it, otherwise you can remove this line
    # payload["updated_at"] = utc_now_iso()

    response = supabase.table("f1_drivers").insert(payload).execute()
    if not response.data:
        raise HTTPException(status_code=400, detail="Failed to create driver")
    return response.data[0]

@app.patch("/drivers/{driver_name}")
async def update_driver(driver_name: str, driver: DriverUpdate, api_key: str = Depends(require_api_key)):
    update_data = driver.model_dump(exclude_none=True)
    
    if "birthdate" in update_data:
        update_data["birthdate"] = update_data["birthdate"].isoformat()

    if not update_data:
        raise HTTPException(status_code=400, detail="No fields provided for update")

    response = supabase.table("f1_drivers").update(update_data).eq("driver_name", driver_name).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Driver not found")
    return response.data[0]

@app.delete("/drivers/{driver_name}")
async def delete_driver(driver_name: str, api_key: str = Depends(require_api_key)):
    response = supabase.table("f1_drivers").delete().eq("driver_name", driver_name).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Driver not found")
    return {"message": f"Driver {driver_name} deleted successfully"}
