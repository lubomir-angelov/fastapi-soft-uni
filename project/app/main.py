# project/app/main.py


from fastapi import FastAPI
# setup 2
from fastapi import Depends

from app.config import get_settings, Settings

app = FastAPI()


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
