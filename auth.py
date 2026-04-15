# Session state — holds the currently logged-in user
_current_user = None


def set_user(user: dict):
    global _current_user
    _current_user = user


def get_user() -> dict:
    return _current_user


def get_role() -> str:
    return _current_user["role"] if _current_user else ""


def get_username() -> str:
    return _current_user["username"] if _current_user else ""


def logout():
    global _current_user
    _current_user = None


def is_admin() -> bool:
    return get_role() == "admin"


def is_cashier() -> bool:
    return get_role() in ("admin", "cashier")
