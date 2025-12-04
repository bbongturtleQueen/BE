from fastapi import APIRouter
from pydantic import BaseModel
from ..db import get_connection

set_api = APIRouter(prefix="/ppang/set")

class CreateSet(BaseModel):
    name: str
    teacher_id: str

class AddProblem(BaseModel):
    set_name: str
    question: str
    answer: str
    choices: list

# 세트 생성
@set_api.post("/create")
def create_set(data: CreateSet):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO sets (name, teacher_id) VALUES (%s, %s)",
            (data.name, data.teacher_id)
        )
        conn.commit()

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        cur.close()
        conn.close()

    return {
        "status": "success",
        "set_name": data.name
    }

# 문제 추가
@set_api.post("/add-problem")
def add_problem(data: AddProblem):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO problems (set_name, question, answer, choices) VALUES (%s, %s, %s, %s)",
            (data.set_name, data.question, data.answer, str(data.choices))
        )
        conn.commit()

    except Exception as e:
        return {"status": "error", "message": str(e)}

    finally:
        cur.close()
        conn.close()

    return {"status": "success"}

# 특정 세트의 문제 목록 조회
@set_api.get("/problems/{set_name}")
def get_problems(set_name: str):
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute(
        "SELECT id, question, answer, choices FROM problems WHERE set_name = %s",
        (set_name,)
    )
    problems = cur.fetchall()

    for p in problems:
        try:
            p["choices"] = eval(p["choices"])
        except:
            p["choices"] = []

    cur.close()
    conn.close()

    return {"problems": problems}