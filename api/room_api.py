from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List
from ..db import get_connection
from typing import Optional

room_api = APIRouter(prefix="/ppang/room")

# ------------------------------
# 세트 목록 조회용 모델
# ------------------------------
class SetOut(BaseModel):
    name: str
    teacher_id: str
    code: Optional[str]  # 방 코드

# ------------------------------
# 방 코드 저장 모델
# ------------------------------
class RoomCodeIn(BaseModel):
    set_name: str
    code: str  # 프론트에서 생성해서 전달

# ------------------------------
# 세트에 방 코드 저장
# ------------------------------
@room_api.post("/create-code")
def create_room_code(data: RoomCodeIn):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO rooms (code, set_name) VALUES (%s, %s)",
                (data.code, data.set_name)
            )
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    return {"status": "success", "set_name": data.set_name, "room_code": data.code}

# ------------------------------
# 세트 목록 + 방 코드 조회 (특정 teacher_id만)
# ------------------------------
@room_api.get("/list", response_model=List[SetOut])
def get_set_list(teacher_id: str = Query(...)):
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT s.name, s.teacher_id, r.code AS room_code
                FROM sets s
                LEFT JOIN rooms r ON s.name = r.set_name
                WHERE s.teacher_id = %s
            """, (teacher_id,))
            sets = cur.fetchall()

            # SetOut 모델에 맞춰서 반환
            result = []
            for s in sets:
                result.append({
                    "name": s["name"],
                    "teacher_id": s["teacher_id"],
                    "code": s["room_code"]  # room code 반환, 없으면 None
                })
            return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

