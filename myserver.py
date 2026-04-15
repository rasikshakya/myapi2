import os
from fastapi import FastAPI, Header, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel

app = FastAPI()

# 1. Fetch the secret key from your Render Environment Variables
# This must match the 'Key' column in your Render screenshot exactly
API_KEY_NAME = "YOUR_SUPER_SECRET_KEY"
ACTUAL_API_KEY = os.getenv(API_KEY_NAME)

# 2. Define the security dependency
def verify_api_key(authorization: str = Header(None)):
    """
    Validates that the incoming request has the correct Bearer token.
    """
    # Check if header exists
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization Header")
    
    # Check if the token matches 'Bearer scuderiaferrari'
    expected_format = f"Bearer {ACTUAL_API_KEY}"
    if authorization != expected_format:
        raise HTTPException(status_code=401, detail="Invalid Authorization Token")
    
    return authorization

# 3. Apply the security to your 'Write' methods (POST, PATCH, DELETE)
@app.post("/drivers", status_code=201)
async def create_driver(driver: DriverCreate, auth: str = Depends(verify_api_key)):
    # Your Supabase insertion logic goes here
    # Example: response = supabase.table("f1_drivers").insert(driver.dict()).execute()
    return {"message": f"Driver {driver.driver_name} added to the grid!"}

@app.patch("/drivers/{driver_name}")
async def update_driver(driver_name: str, updates: DriverUpdate, auth: str = Depends(verify_api_key)):
    # Your Supabase update logic goes here
    return {"message": f"Updated details for {driver_name}"}

@app.delete("/drivers/{driver_name}")
async def delete_driver(driver_name: str, auth: str = Depends(verify_api_key)):
    # Your Supabase delete logic goes here
    return {"message": f"Driver {driver_name} removed from the registry"}
