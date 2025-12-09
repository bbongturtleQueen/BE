from fastapi import APIRouter
from pydantic import BaseModel
from ..db import get_connection
import hashlib


teacher_api = APIRouter()

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def verify_password(password: str, hashed: str) -> bool:
    return hash_password(password) == hashed

class Teacher(BaseModel):
    id: str
    password: str

class LoginRequest(BaseModel):
    id: str
    password: str

class CreateRoomRequest(BaseModel):   # ★ 추가
    id: str

# 회원가입
@teacher_api.post("/ppang/tch/turtle/signup")
def register_teacher(t: Teacher):
    conn = get_connection()
    cur = conn.cursor()

    hashed_pw = hash_password(t.password)

    try:
        cur.execute(
            "INSERT INTO teachers (id, password) VALUES (%s, %s)",
            (t.id, hashed_pw)
        )
        conn.commit()
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        cur.close()
        conn.close()

    return {"status": "success", "id": t.id}

# 로그인
@teacher_api.post("/ppang/tch/turtle/login")
def login_teacher(data: LoginRequest):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("SELECT * FROM teachers WHERE id = %s", (data.id,))
    teacher = cur.fetchone()

    cur.close()
    conn.close()

    if not teacher:
        return {"status": "not_found"}

    if verify_password(data.password, teacher["password"]):
        return {"status": "success"}

    return {"status": "wrong_password"}