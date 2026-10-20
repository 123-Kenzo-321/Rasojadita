"""Local database layer for Rasojadita Art Commissions.

Data is stored as JSON in the browser's localStorage (persistent) or
sessionStorage (login session when "Remember me" is off), accessed from
Python through PyScript. Outside the browser (for example when running
tests) it falls back to an in-memory store, so this module can be tested
with plain Python.

Tables
------
users    : [{id, fullname, email, username, salt, password_hash, role, created_at}]
messages : [{id, user_id, name, email, product, is_student, text, status, created_at}]
session  : user id of the logged-in user
"""
import json
import time

PREFIX = "rasojadita:"


class _MemoryStorage:
    """Minimal stand-in for window.localStorage when not running in a browser."""

    def __init__(self):
        self._data = {}

    def getItem(self, key):
        return self._data.get(key)

    def setItem(self, key, value):
        self._data[key] = value

    def removeItem(self, key):
        self._data.pop(key, None)


def _get_storages():
    try:
        from pyscript import window
        return window.localStorage, window.sessionStorage
    except Exception:
        return _MemoryStorage(), _MemoryStorage()


_local, _session = _get_storages()


def _read(storage, key, default):
    raw = storage.getItem(PREFIX + key)
    if raw is None:
        return default
    try:
        return json.loads(raw)
    except ValueError:
        return default


def _write(storage, key, value):
    storage.setItem(PREFIX + key, json.dumps(value))


def _next_id(rows):
    return max((row["id"] for row in rows), default=0) + 1


# ---------------------------------------------------------------- users
def get_users():
    return _read(_local, "users", [])


def save_users(users):
    _write(_local, "users", users)


def find_user_by_id(user_id):
    for user in get_users():
        if user["id"] == user_id:
            return user
    return None


def find_user_by_username(username):
    wanted = (username or "").strip().lower()
    for user in get_users():
        if user["username"].lower() == wanted:
            return user
    return None


def find_user_by_email(email):
    wanted = (email or "").strip().lower()
    for user in get_users():
        if user["email"].lower() == wanted:
            return user
    return None


def add_user(fullname, email, username, salt, password_hash, role="customer"):
    users = get_users()
    user = {
        "id": _next_id(users),
        "fullname": fullname,
        "email": email.lower(),
        "username": username,
        "salt": salt,
        "password_hash": password_hash,
        "role": role,
        "created_at": time.time(),
    }
    users.append(user)
    save_users(users)
    return user


# ------------------------------------------------------------- messages
def get_messages():
    return _read(_local, "messages", [])


def add_message(user_id, name, email, product, is_student, text):
    messages = get_messages()
    message = {
        "id": _next_id(messages),
        "user_id": user_id,
        "name": name,
        "email": email.lower(),
        "product": product,
        "is_student": bool(is_student),
        "text": text,
        "status": "new",
        "created_at": time.time(),
    }
    messages.append(message)
    _write(_local, "messages", messages)
    return message


def set_message_status(message_id, status):
    messages = get_messages()
    for message in messages:
        if message["id"] == message_id:
            message["status"] = status
    _write(_local, "messages", messages)


def delete_message(message_id):
    messages = [m for m in get_messages() if m["id"] != message_id]
    _write(_local, "messages", messages)


# -------------------------------------------------------------- session
def set_session(user_id, remember=False):
    """Remember me -> localStorage (survives closing the browser);
    otherwise sessionStorage (cleared when the tab is closed)."""
    clear_session()
    target = _local if remember else _session
    _write(target, "session", user_id)


def get_session():
    user_id = _read(_session, "session", None)
    if user_id is None:
        user_id = _read(_local, "session", None)
    return user_id


def clear_session():
    _session.removeItem(PREFIX + "session")
    _local.removeItem(PREFIX + "session")
