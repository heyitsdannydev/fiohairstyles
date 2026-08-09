import logging
import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mangum import Mangum

from app.routers import appointment, auth, client, service

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fiohairstyles_api")

app = FastAPI(title="fiohairstyles-api")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info("%s %s -> %s", request.method, request.url.path, response.status_code)
    return response


# The session token travels as a plain Authorization header, not a cookie
# (see app/auth.py), so no allow_credentials is needed here.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[os.environ.get("ALLOWED_ORIGIN", "http://localhost:3000")],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(client.router)
app.include_router(appointment.router)
app.include_router(service.router)

handler = Mangum(app)
