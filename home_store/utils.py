import uuid

def generate_reset_token():
    return str(uuid.uuid4())