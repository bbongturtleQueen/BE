from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import get_connection
import random
import string

set_api = APIRouter(prefix="/ppang/set")


# ------------------------------
# Pydantic 모델
# ------------------------------
class CreateSet(BaseModel):
    name: str
    teacher_id: str


# ------------------------------
# 랜덤 코드 생성 (숫자 6자리)
# ------------------------------
def generate_room_code(length: int = 6) -> str:
    chars = string.digits  # 숫자만
    return ''.join(random.choice(chars) for _ in range(length))



# ------------------------------
# 세트 생성 + 방 코드 생성
# ------------------------------
@set_api.post("/create")
def create_set(data: CreateSet):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 세트 생성
            cur.execute(
                "INSERT INTO sets (name, teacher_id) VALUES (%s, %s)",
                (data.name, data.teacher_id)
            )

            # 랜덤 코드 생성
            code = generate_room_code()
            while True:
                cur.execute("SELECT code FROM rooms WHERE code = %s", (code,))
                if cur.fetchone() is None:
                    break
                code = generate_room_code()

            # rooms에 저장
            cur.execute(
                "INSERT INTO rooms (code, set_name) VALUES (%s, %s)",
                (code, data.name)
            )

            conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

    return {"status": "success", "set_name": data.name, "room_code": code}
