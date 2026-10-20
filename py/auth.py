"""Registration, login and session logic (no DOM code, so it is testable).

NOTE: this is a client-side coursework demo. Passwords are salted and hashed
before being stored, but anything kept in the browser can be inspected by
whoever uses that browser. A real shop would verify logins on a server.
"""
import hashlib
import os
import re

import db

ADMIN_USERNAME = "admin"
ADMIN_EMAIL = "artist@rasojadita.local"
ADMIN_PASSWORD = "Admin@123"
RESERVED_USERNAMES = {"admin", "administrator", "artist", "rasojadita", "root", "support"}

ROUNDS = 20000
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
USERNAME_RE = re.compile(r"^[A-Za-z0-9_]{3,20}$")


# ------------------------------------------------------------- hashing
def make_salt():
    return os.urandom(16).hex()


def hash_password(password, salt):
    salt_bytes = bytes.fromhex(salt)
    digest = salt_bytes + password.encode("utf-8")
    for _ in range(ROUNDS):
        digest = hashlib.sha256(digest + salt_bytes).digest()
    return digest.hex()


# ---------------------------------------------------------- validation
def clean_name(value):
    return " ".join((value or "").split())


def password_strength(password):
    """Return (score 0-4, label) for the live strength meter."""
    if not password:
        return 0, ""
    score = 0
    if len(password) >= 8:
        score += 1
    if len(password) >= 12:
        score += 1
    if re.search(r"[a-z]", password) and re.search(r"[A-Z]", password):
        score += 1
    if re.search(r"\d", password) and re.search(r"[^A-Za-z0-9]", password):
        score += 1
    labels = {0: "Too weak", 1: "Weak", 2: "Fair", 3: "Good", 4: "Strong"}
    return score, labels[score]


def check_username(username):
    """Return an error message, or '' if the username is valid and free."""
    username = (username or "").strip()
    if not username:
        return "Username is required."
    if not USERNAME_RE.match(username):
        return "Use 3-20 letters, numbers or underscores."
    if username.lower() in RESERVED_USERNAMES or db.find_user_by_username(username):
        return "That username is already taken."
    return ""


def validate_registration(fullname, email, username, password, confirm):
    """Return {field: message}; an empty dict means everything is valid."""
    errors = {}
    fullname = clean_name(fullname)
    email = (email or "").strip()

    if len(fullname) < 2:
        errors["fullname"] = "Please enter your full name."
    elif len(fullname) > 60:
        errors["fullname"] = "Full name is too long (60 characters max)."

    if not email:
        errors["email"] = "Email is required."
    elif not EMAIL_RE.match(email):
        errors["email"] = "Enter a valid email address."
    elif db.find_user_by_email(email):
        errors["email"] = "An account with this email already exists."

    username_error = check_username(username)
    if username_error:
        errors["username"] = username_error

    if not password:
        errors["password"] = "Password is required."
    elif len(password) < 8:
        errors["password"] = "Password must be at least 8 characters."
    elif not (re.search(r"[A-Za-z]", password) and re.search(r"\d", password)):
        errors["password"] = "Include at least one letter and one number."

    if not confirm:
        errors["confirm"] = "Please confirm your password."
    elif password != confirm:
        errors["confirm"] = "Passwords do not match."

    return errors


# --------------------------------------------------------- operations
def register(fullname, email, username, password, confirm):
    """Create a customer account. Returns (user, errors)."""
    errors = validate_registration(fullname, email, username, password, confirm)
    if errors:
        return None, errors
    salt = make_salt()
    user = db.add_user(
        clean_name(fullname),
        email.strip(),
        username.strip(),
        salt,
        hash_password(password, salt),
        role="customer",
    )
    return user, {}


def login(identifier, password, remember=False):
    """Log in with username OR email. Returns (user, error_message)."""
    identifier = (identifier or "").strip()
    if not identifier or not password:
        return None, "Enter your username (or email) and password."
    user = db.find_user_by_username(identifier) or db.find_user_by_email(identifier)
    # Same message for unknown user and wrong password on purpose.
    if not user or hash_password(password, user["salt"]) != user["password_hash"]:
        return None, "Invalid username/email or password."
    db.set_session(user["id"], remember)
    return user, ""


def current_user():
    user_id = db.get_session()
    if user_id is None:
        return None
    user = db.find_user_by_id(user_id)
    if user is None:
        db.clear_session()
    return user


def logout():
    db.clear_session()


def ensure_seed_admin():
    """Create the seeded artist/admin account on first run."""
    if db.find_user_by_username(ADMIN_USERNAME):
        return
    salt = make_salt()
    db.add_user(
        "Rasojadita Artist",
        ADMIN_EMAIL,
        ADMIN_USERNAME,
        salt,
        hash_password(ADMIN_PASSWORD, salt),
        role="admin",
    )
