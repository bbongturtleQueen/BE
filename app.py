from fastapi import FastAPI
from BE.api.teacher_api import teacher_api
from BE.api.kid_api import kid_api
from fastapi.middleware.cors import CORSMiddleware
from BE.websocket import ws_router
from BE.api.set_api import set_api


app = FastAPI()

app.include_router(ws_router)
app.include_router(kid_api)
app.include_router(teacher_api)
app.include_router(set_api)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"message": "FastAPI server running!"}