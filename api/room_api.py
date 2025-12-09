from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List
from ..db import get_connection

room_api = APIRouter(prefix="/ppang/room")  # /ppang/room/list 등으로 호출

# 세트 목록 조회용 모델
class SetOut(BaseModel):
    name: str
    teacher_id: str
    code: str  # 방 코드

# 세트 목록 + 방 코드 조회
@room_api.get("/list", response_model=List[SetOut])
def get_set_list():
    conn = get_connection()
    try:
        with conn.cursor(dictionary=True) as cur:
            cur.execute("""
                SELECT s.name, s.teacher_id, r.code
                FROM sets s
                LEFT JOIN rooms r ON s.name = r.set_name
            """)
            sets = cur.fetchall()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    return sets