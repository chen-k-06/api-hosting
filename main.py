from fastapi import FastAPI
from Wordle.routes import router as Wordle_router

app = FastAPI()

app.include_router(Wordle_router, prefix="/Wordle")
