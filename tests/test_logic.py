"""Plain-Python tests for db.py and auth.py (run: python tests/test_logic.py)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "py"))

import auth  # noqa: E402
import db  # noqa: E402


def reset():
    db._local._data.clear()
    db._session._data.clear()


def test_seed_admin_once():
    reset()
    auth.ensure_seed_admin()
    auth.ensure_seed_admin()
    users = db.get_users()
    assert len(users) == 1 and users[0]["role"] == "admin"
    assert auth.ADMIN_PASSWORD not in str(users)  # password never stored in plain text


def test_register_validation():
    reset()
    auth.ensure_seed_admin()
    errors = auth.validate_registration("", "bad", "a", "short", "other")
    assert set(errors) == {"fullname", "email", "username", "password", "confirm"}
    assert "taken" in auth.validate_registration("Ann Lee", "ann@x.com", "ADMIN", "abcdefg1", "abcdefg1")["username"]
    assert "letter" in auth.validate_registration("Ann Lee", "ann@x.com", "ann_lee", "12345678", "12345678")["password"]
    assert auth.validate_registration("Ann Lee", "ann@x.com", "ann_lee", "abcdefg1", "abcdefg1") == {}


def test_register_and_duplicates():
    reset()
    user, errors = auth.register("  Ann   Lee ", "Ann@X.com", "ann_lee", "abcdefg1", "abcdefg1")
    assert user and not errors
    assert user["fullname"] == "Ann Lee" and user["email"] == "ann@x.com" and user["role"] == "customer"
    _, errors = auth.register("Ann Two", "ANN@x.com", "ann_two", "abcdefg1", "abcdefg1")
    assert "email" in errors
    _, errors = auth.register("Ann Two", "two@x.com", "Ann_Lee", "abcdefg1", "abcdefg1")
    assert "username" in errors


def test_login_logout_and_remember():
    reset()
    auth.register("Ann Lee", "ann@x.com", "ann_lee", "abcdefg1", "abcdefg1")
    assert auth.login("ann_lee", "wrong", False)[0] is None
    assert auth.login("nobody", "abcdefg1", False)[0] is None
    assert auth.login("", "", False)[1]
    user, err = auth.login("ANN@x.com", "abcdefg1", False)  # by email, any case
    assert user and not err and auth.current_user()["username"] == "ann_lee"
    assert db._session.getItem(db.PREFIX + "session") is not None
    assert db._local.getItem(db.PREFIX + "session") is None  # not remembered
    auth.logout()
    assert auth.current_user() is None
    auth.login("ann_lee", "abcdefg1", True)
    assert db._local.getItem(db.PREFIX + "session") is not None  # remembered
    auth.logout()
    assert auth.current_user() is None


def test_admin_login():
    reset()
    auth.ensure_seed_admin()
    user, err = auth.login(auth.ADMIN_USERNAME, auth.ADMIN_PASSWORD, False)
    assert user and user["role"] == "admin"


def test_stale_session_cleared():
    reset()
    db.set_session(999, True)
    assert auth.current_user() is None
    assert db.get_session() is None


def test_messages():
    reset()
    m1 = db.add_message(None, "Guest", "G@x.com", "Poster", False, "Hello there poster")
    m2 = db.add_message(1, "Ann", "ann@x.com", "Solo portrait", True, "Please draw me")
    assert (m1["id"], m2["id"]) == (1, 2) and m1["email"] == "g@x.com"
    db.set_message_status(1, "done")
    assert db.get_messages()[0]["status"] == "done"
    db.delete_message(1)
    assert [m["id"] for m in db.get_messages()] == [2]
    db.delete_message(2)
    assert db.add_message(None, "N", "n@x.com", "Poster", False, "again again")["id"] == 1


def test_password_strength_and_username():
    assert auth.password_strength("")[0] == 0
    assert auth.password_strength("abc")[0] == 0
    assert auth.password_strength("abcdefgh")[0] == 1
    assert auth.password_strength("Abcdefg1!xyz")[0] == 4
    reset()
    assert auth.check_username("ab")
    assert auth.check_username("ok_name") == ""
    assert auth.check_username("bad name!")


def test_hash_is_salted():
    s1, s2 = auth.make_salt(), auth.make_salt()
    assert s1 != s2
    assert auth.hash_password("pw12345678", s1) != auth.hash_password("pw12345678", s2)
    assert auth.hash_password("pw12345678", s1) == auth.hash_password("pw12345678", s1)


if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    for t in tests:
        t()
        print("PASS", t.__name__)
    print(f"{len(tests)} tests passed")
