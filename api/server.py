from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from api.routes import router
import os

app = FastAPI(
    title="Gitcast API",
    description="Cloud backend for Gitcast",
    version="1.0.0",
)

@app.exception_handler(RequestValidationError)
async def validation_handler(
        request: Request,
        exc: RequestValidationError):
    print(f"[422] Validation error: {exc.errors()}")
    print(f"[422] Body: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors()})

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "version": "1.0.0",
        "providers": {
            "groq": bool(os.getenv("GROQ_API_KEY")),
            "gemini": bool(os.getenv("GEMINI_API_KEY")),
            "openrouter": bool(
                os.getenv("OPENROUTER_API_KEY")),
            "cerebras": bool(
                os.getenv("CEREBRAS_API_KEY")),
        },
        "supabase": bool(os.getenv("SUPABASE_URL")),
    }
