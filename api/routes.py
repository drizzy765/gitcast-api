from fastapi import APIRouter, HTTPException, Header
from pydantic import BaseModel, ConfigDict
from typing import Optional, Any
from api.generate import generate_posts
from api.auth import get_or_create_session
from storage.supabase_client import (
    save_post, get_posts, update_post)
import os

router = APIRouter()

# ── Request models ────────────────────────────────

class GenerateRequest(BaseModel):
    model_config = ConfigDict(extra="allow")

    raw_thought: str = ""
    ocr_text: Optional[str] = ""
    git_diff: Optional[str] = ""
    git_diff_available: Optional[bool] = False
    narrative: Optional[str] = ""
    use_vision_fallback: Optional[bool] = False
    screenshot_b64: Optional[str] = None
    user_message: Optional[str] = ""
    format_keys: Optional[list] = [
        "x_post", "linkedin",
        "pr_desc", "quick_win"]
    byok_key: Optional[str] = None
    byok_provider: Optional[str] = None
    project_context: Optional[str] = ""
    readme_content: Optional[str] = ""
    tech_stack: Optional[str] = ""

class SavePostRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    post_text: str
    format_key: str
    platform: Optional[str] = "twitter"
    tweet_url: Optional[str] = ""
    tweet_id: Optional[str] = ""
    session_id: Optional[str] = ""

class UpdatePostRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    post_id: str
    session_id: str
    posted_verified: Optional[bool] = None
    declined: Optional[bool] = None
    impressions: Optional[int] = None
    likes: Optional[int] = None
    comments: Optional[int] = None
    reposts: Optional[int] = None

class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    instruction: str
    current_post: str
    format_key: str
    byok_key: Optional[str] = None
    byok_provider: Optional[str] = None

class ArticleRequest(BaseModel):
    model_config = ConfigDict(extra="allow")
    sprint_log: Optional[list] = []
    narrative: Optional[str] = ""
    readme_content: Optional[str] = ""
    project_context: Optional[str] = ""
    byok_key: Optional[str] = None
    byok_provider: Optional[str] = None

# ── Session ───────────────────────────────────────

@router.post("/api/session")
async def create_session():
    session_id = get_or_create_session()
    return {"session_id": session_id}

# ── Generate ──────────────────────────────────────

@router.post("/api/generate")
async def generate(request: GenerateRequest):
    if not request.raw_thought:
        raise HTTPException(
            status_code=400,
            detail="raw_thought is required")
    try:
        results = await generate_posts(
            payload=request.dict())
        return {"success": True, "variations": results}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=str(e))

# ── Chat refinement ───────────────────────────────

@router.post("/api/chat")
async def chat(request: ChatRequest):
    if not request.current_post:
        raise HTTPException(
            status_code=400,
            detail="current_post is required")
    if not request.instruction:
        raise HTTPException(
            status_code=400,
            detail="instruction is required")
    try:
        from api.generate import refine_post
        refined = await refine_post(
            current_post=request.current_post,
            instruction=request.instruction,
            format_key=request.format_key,
            byok_key=request.byok_key,
            byok_provider=request.byok_provider,
        )
        return {"success": True, "refined_post": refined}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=str(e))

# ── Article endpoints ─────────────────────────────

@router.post("/api/article/generate")
async def generate_article(request: ArticleRequest):
    try:
        from api.generate import generate_article
        result = await generate_article(
            request.dict())
        return {"success": True, "article": result}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=str(e))

@router.post("/api/article/refine")
async def refine_article(request: ChatRequest):
    try:
        from api.generate import refine_post
        result = await refine_post(
            current_post=request.current_post,
            instruction=request.instruction,
            format_key="article",
            byok_key=request.byok_key,
            byok_provider=request.byok_provider,
        )
        return {"success": True, "article": result}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=str(e))

# ── Storage ───────────────────────────────────────

@router.post("/api/posts/save")
async def save(request: SavePostRequest):
    try:
        result = await save_post(request.dict())
        return {"success": True, "post": result}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=str(e))

@router.get("/api/posts/{session_id}")
async def get(session_id: str):
    try:
        posts = await get_posts(session_id)
        return {"success": True, "posts": posts}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=str(e))

@router.patch("/api/posts/update")
async def update(request: UpdatePostRequest):
    try:
        result = await update_post(request.dict())
        return {"success": True, "post": result}
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=str(e))

# ── Keys status ───────────────────────────────────

@router.get("/api/keys/status")
async def keys_status(
        x_byok_key: Optional[str] = Header(None),
        x_byok_provider: Optional[str] = Header(None)):
    base_configured = {
        "groq": bool(os.getenv("GROQ_API_KEY")),
        "gemini": bool(os.getenv("GEMINI_API_KEY")),
        "openrouter": bool(
            os.getenv("OPENROUTER_API_KEY")),
        "cerebras": bool(
            os.getenv("CEREBRAS_API_KEY")),
    }
    has_base = any(base_configured.values())
    has_byok = bool(x_byok_key)
    return {
        "base_keys": base_configured,
        "has_base_keys": has_base,
        "has_byok": has_byok,
        "byok_provider": x_byok_provider
            if has_byok else None,
        "using_base": not has_byok,
        "message": (
            "Using your own key" if has_byok
            else "Using Gitcast shared key "
                 "[rate limits apply]"
        )
    }
