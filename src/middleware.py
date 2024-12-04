from fastapi import FastAPI, Request
import time
from logging import getLogger
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

logger = getLogger("uvicorn.access")


def register_middleware(app: FastAPI):

    @app.middleware("http")
    async def custom_logging(request: Request, call_next):
        start_time = time.time()

        response = await call_next(request)

        processing_time = time.time() - start_time
        message = f"{request.method} - {request.url.path} -> {response.status_code} : Completed in {processing_time}s"
        print(message)
        return response

    # Updated CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            "http://localhost",
            "http://127.0.0.1",
            "https://bookly-fastapi-p5dd.onrender.com",
        ],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=True,
    )

    # Updated TrustedHost configuration
    app.add_middleware(
        TrustedHostMiddleware,
        allowed_hosts=[
            "localhost",
            "127.0.0.1",
            "bookly-fastapi-p5dd.onrender.com",
            "*.onrender.com",  # Wildcard for subdomains
        ],
    )
