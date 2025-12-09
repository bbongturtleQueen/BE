from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import get_connection

student_api = APIRouter(prefix="/ppang/kid")

class EnterCode(BaseModel):
    code: str

@student_api.post("/enter-code")
def enter_code(data: EnterCode):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 방 코드 확인
            cur.execute("SELECT code FROM rooms WHERE code = %s", (data.code,))
            room = cur.fetchone()
            if not room:
                return {"status": "invalid"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        conn.close()

    return {"status": "valid"}