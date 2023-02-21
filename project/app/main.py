# project/app/main.py

import os

from fastapi import FastAPI
# setup 2
from fastapi import Depends
# tortoise
from tortoise.contrib.fastapi import register_tortoise

from app.config import get_settings, Settings
app = FastAPI()


register_tortoise(
    app,
    db_url=os.environ.get("DATABASE_URL"),
    modules={"models": ["app.models.tortoise"]},
    generate_schemas=False,
    add_exception_handlers=True,
)

@app.get("/ping")
# def pong():
# setup 2
async def pong(settings: Settings = Depends(get_settings)):
    return {
            "ping": "pong!",
            # setup 2
            "environment": settings.environment,
            "testing": settings.testing
            }
