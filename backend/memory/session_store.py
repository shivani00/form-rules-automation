session_store = {}


def get_session(session_id: str):
    if session_id not in session_store:
        session_store[session_id] = {}
    return session_store[session_id]


def update_session(session_id: str, data: dict):
    session = get_session(session_id)
    session.update(data)
    return session


def clear_session(session_id: str):
    if session_id in session_store:
        del session_store[session_id]