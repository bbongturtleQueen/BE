from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from ..db import get_connection

set_api = APIRouter(prefix="/ppang/set")

# ------------------------------
# Pydantic 모델
# ------------------------------
class CreateSet(BaseModel):
    name: str
    teacher_id: str

# ------------------------------
# 세트 생성만
# ------------------------------
@set_api.post("/create")
def create_set(data: CreateSet):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO sets (name, teacher_id) VALUES (%s, %s)",
                (data.name, data.teacher_id)
            )
            conn.commit()
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()

    return {
        "status": "success",
        "set_name": data.name
    }