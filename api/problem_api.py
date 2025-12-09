from fastapi import APIRouter, HTTPException, Request
from ..db import get_connection
import json

problem_api = APIRouter(prefix="/ppang/problem")

# ------------------------------
# 문제 추가
# ------------------------------
@problem_api.post("/add")
async def add_problem(request: Request):
    data = await request.json()

    required_fields = ["set_name", "question", "answer", "choices"]
    for field in required_fields:
        if field not in data:
            raise HTTPException(status_code=400, detail=f"'{field}' is required")

    set_name = data["set_name"]
    question = data["question"]
    answer = data["answer"]
    choices = data["choices"]

    if not isinstance(choices, list):
        raise HTTPException(status_code=400, detail="'choices' must be a list")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO problems (set_name, question, answer, choices) VALUES (%s, %s, %s, %s)",
                (set_name, question, answer, json.dumps(choices))
            )
            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

    return {"status": "success"}

# ------------------------------
# 특정 세트 문제 전체 조회
# ------------------------------
@problem_api.get("/list/{set_name}")
def get_problems(set_name: str):
    """
    특정 세트(set_name)의 모든 문제를 반환
    프론트에서 하나씩 화면에 표시 가능
    """
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute(
                "SELECT id, question, answer, choices FROM problems WHERE set_name = %s ORDER BY id ASC",
                (set_name,)
            )
            problems = cur.fetchall()

        # choices를 JSON 문자열에서 리스트로 변환
        for p in problems:
            try:
                p["choices"] = json.loads(p["choices"])
            except:
                p["choices"] = []

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    return {"problems": problems}