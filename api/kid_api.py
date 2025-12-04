from fastapi import APIRouter
from pydantic import BaseModel
from ..db import get_connection

from ..room_api import join_room, get_kids   # ★ 추가

kid_api = APIRouter(prefix="/ppang/kid")

class Kid(BaseModel):
    id: str

class Score(BaseModel):
    user_id: str
    score: int


# 아이 아이디
@kid_api.post("/register")
def register_kid(kid: Kid):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute("INSERT INTO kids (id) VALUES (%s)", (kid.id,))
        conn.commit()
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        cur.close()
        conn.close()

    return {"status": "success", "id": kid.id}

# 점수 저장
@kid_api.post("/score")
def save_score(score: Score):
    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            "INSERT INTO scores (user_id, score) VALUES (%s, %s) "
            "ON DUPLICATE KEY UPDATE score = %s",
            (score.user_id, score.score, score.score)
        )
        conn.commit()
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        cur.close()
        conn.close()

    return {"status": "success", "user_id": score.user_id}

# 랭킹 조회
@kid_api.get("/rank")
def get_rank():
    conn = get_connection()
    cur = conn.cursor(dictionary=True)

    cur.execute("""
        SELECT kids.id, scores.score
        FROM scores
        JOIN kids ON scores.user_id = kids.id
        ORDER BY scores.score DESC
    """)

    ranking = cur.fetchall()

    cur.close()
    conn.close()
    return {"rank": ranking}


# 초대코드 확인
class EnterCode(BaseModel):
    code: str
    id: str

@kid_api.post("/enter-code")
def enter_code(data: EnterCode):

    ok = join_room(data.code, data.id)

    if not ok:
        return {"status": "invalid"}

    kids = get_kids(data.code)

    return {
        "status": "valid",
        "kids": kids
    }