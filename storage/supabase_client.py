import os
from datetime import datetime

def get_client():
    url = os.getenv("SUPABASE_URL", "")
    key = os.getenv("SUPABASE_SERVICE_KEY", "")
    if not url or not key:
        return None
    try:
        from supabase import create_client
        return create_client(url, key)
    except Exception:
        return None

async def save_post(post_data: dict) -> dict:
    client = get_client()
    if not client:
        return post_data
    try:
        post_data["timestamp"] = datetime.utcnow().isoformat()
        result = client.table("posts").insert(
            post_data).execute()
        return result.data[0] if result.data else post_data
    except Exception as e:
        print(f"[Storage] save_post failed: {e}")
        return post_data

async def get_posts(session_id: str) -> list:
    client = get_client()
    if not client:
        return []
    try:
        result = client.table("posts").select(
            "*").eq("session_id", session_id
            ).order("timestamp", desc=True).execute()
        return result.data or []
    except Exception as e:
        print(f"[Storage] get_posts failed: {e}")
        return []

async def update_post(post_data: dict) -> dict:
    client = get_client()
    if not client:
        return post_data
    try:
        post_id = post_data.pop("post_id")
        result = client.table("posts").update(
            post_data).eq("id", post_id).execute()
        return result.data[0] if result.data else post_data
    except Exception as e:
        print(f"[Storage] update_post failed: {e}")
        return post_data
