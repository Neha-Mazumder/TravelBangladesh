# AI citation: GitHub Copilot helped structure this decorator pattern, based on CS50 Finance
from functools import wraps
from flask import redirect, session


def login_required(f):
    """Decorator that redirects to login if user is not authenticated."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if session.get("user_id") is None:
            return redirect("/login")
        return f(*args, **kwargs)
    return decorated
