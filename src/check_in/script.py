if __name__ == "__main__":
    from __init__ import session_id
    from api import JuejinSession

    session = JuejinSession(session_id)
    if not session.is_checked_in():
        session.check_in()
        print("Check in successfully.")
    else:
        print("Already checked in. Aborted.")
