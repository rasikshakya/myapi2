from fastapi import FastAPI
from supabase import create_client, Client
import os

app = FastAPI()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

@app.get("/")
async def root():
    response = supabase.table("president").select("*", count="exact").execute()
    return {
        "message": "Hello World",
        "president_count": response.count
    }
