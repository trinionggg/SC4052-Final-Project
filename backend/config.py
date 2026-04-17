import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

ENV_RIOT_KEY   = os.getenv("RIOT_API_KEY", "")
ENV_OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")

def create_app() -> FastAPI:
    app = FastAPI(title="CoachBot-as-a-Service API", version="2.0")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
    )
    return app