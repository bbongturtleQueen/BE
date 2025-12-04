import random

rooms = {}

def generate_code():
    return "".join(random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789") for _ in range(6))

def create_room(teacher_id):
    code = generate_code()
    rooms[code] = {
        "teacher": teacher_id,
        "kids": []
    }
    return code

def join_room(code, kid_id):
    if code not in rooms:
        return False
    rooms[code]["kids"].append(kid_id)
    return True

def get_kids(code):
    if code not in rooms:
        return []
    return rooms[code]["kids"]