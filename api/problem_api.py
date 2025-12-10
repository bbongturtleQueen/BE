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
        print("문제 추가 실패:", e)  # 🔹 콘솔에 에러 로그 찍기
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

    return {"status": "success"}

# ------------------------------
# room code 기준 문제 조회
# ------------------------------
@problem_api.get("/list-by-code/{room_code}")
def get_problems_by_code(room_code: str):
    """
    room_code를 받아 해당 세트(set_name)의 문제를 반환
    """
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            # 1️⃣ room_code로 set_name 조회
            cur.execute("SELECT set_name FROM rooms WHERE code = %s", (room_code,))
            room = cur.fetchone()
            if not room:
                raise HTTPException(status_code=404, detail="Room not found")
            set_name = room["set_name"]

            # 2️⃣ set_name으로 문제 조회
            cur.execute(
                "SELECT id, question, answer, choices FROM problems WHERE set_name = %s ORDER BY id ASC",
                (set_name,)
            )
            problems = cur.fetchall()

            # choices를 JSON 문자열에서 리스트로 변환
            # 백엔드에서 변환 (FastAPI)
            for p in problems:
                try:
                    p["choices"] = json.loads(p["choices"])
                except Exception as e:
                    print(f"choices 파싱 실패 (문제 id {p.get('id')}):", e)
                    p["choices"] = []

                # question 분리
                try:
                    parts = p["question"].split(" ")
                    p["num1"] = int(parts[0])
                    p["operator"] = parts[1]
                    p["num2"] = int(parts[2])
                    p["options"] = p["choices"]
                except Exception as e:
                    print(f"question 분리 실패 (문제 id {p.get('id')}):", e)
                    p["num1"] = 0
                    p["operator"] = "+"
                    p["num2"] = 0
                    p["options"] = p["choices"]

    except Exception as e:
        print("문제 조회 실패:", e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    return {"set_name": set_name, "problems": problems}
