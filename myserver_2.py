import os
from fastapi import FastAPI
from supabase import create_client, Client

app = FastAPI(title="F1 Supabase Connection Test")

# --- SUPABASE CONFIG ---
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

# Create the Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
async def root():
    # This checks the new f1_drivers table instead of the old president table
    try:
        response = supabase.table("f1_drivers").select("*", count="exact").execute()
        return {
            "message": "F1 Connection Successful",
            "table": "f1_drivers",
            "driver_count": response.count
        }
    except Exception as e:
        return {
            "message": "Connection Failed",
            "error": str(e)
        }
