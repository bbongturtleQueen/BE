from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import get_connection

set_api = APIRouter(prefix="/ppang/set")

# 세트 생성 모델
class CreateSet(BaseModel):
    name: str
    teacher_id: str
    room_code: str  # 프론트에서 랜덤 생성해서 전달

# 세트 생성 + 방 코드 저장
@set_api.post("/create")
def create_set(data: CreateSet):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. 세트 생성
            cur.execute(
                "INSERT INTO sets (name, teacher_id) VALUES (%s, %s)",
                (data.name, data.teacher_id)
            )

            # 2. rooms 테이블에 방 코드 저장
            cur.execute(
                "INSERT INTO rooms (code, set_name) VALUES (%s, %s)",
                (data.room_code, data.name)
            )

            conn.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

    return {
        "status": "success",
        "set_name": data.name,
        "room_code": data.room_code
    }