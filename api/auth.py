import uuid

def get_or_create_session() -> str:
    return str(uuid.uuid4())
