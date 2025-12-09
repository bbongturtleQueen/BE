from fastapi import FastAPI
from BE.api.teacher_api import teacher_api
from BE.api.student_api import student_api
from fastapi.middleware.cors import CORSMiddleware
from BE.api.set_api import set_api
from BE.api.room_api import room_api
from BE.api.problem_api import problem_api


app = FastAPI()

app.include_router(student_api)
app.include_router(teacher_api)
app.include_router(set_api)
app.include_router(room_api)
app.include_router(problem_api)

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