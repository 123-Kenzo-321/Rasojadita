"""Register page events: live validation, password strength, submit."""
from pyscript import when

import auth
import db
import ui

if ui.init_page():
    ui.go("account.html")

FIELDS = {
    "fullname": "reg-fullname",
    "email": "reg-email",
    "username": "reg-username",
    "password": "reg-password",
    "confirm": "reg-confirm",
}

STRENGTH_COLORS = {0: "#e5e7eb", 1: "#ef4444", 2: "#f59e0b", 3: "#84cc16", 4: "#10b981"}


def value(field):
    return ui.el(FIELDS[field]).value


# ----------------------------------------------------------- live events
@when("click", ".toggle-pw")
def on_toggle_password(event):
    target = ui.el(event.currentTarget.getAttribute("data-target"))
    showing = target.type == "text"
    target.type = "password" if showing else "text"
    event.currentTarget.textContent = "Show" if showing else "Hide"


@when("input", "#reg-username")
def on_username_input(event):
    hint = ui.el("reg-username-hint")
    username = value("username").strip()
    ui.set_field_error("reg-username", "")
    if not username:
        hint.textContent = ""
        return
    error = auth.check_username(username)
    hint.textContent = error or "Username is available."
    hint.className = "field-hint " + ("bad" if error else "ok")


@when("input", "#reg-password")
def on_password_input(event):
    score, label = auth.password_strength(value("password"))
    bar = ui.el("pw-bar")
    bar.style.width = str(score * 25) + "%"
    bar.style.backgroundColor = STRENGTH_COLORS[score]
    ui.el("pw-label").textContent = label
    ui.set_field_error("reg-password", "")
    on_confirm_input(None)


@when("input", "#reg-confirm")
def on_confirm_input(event):
    hint = ui.el("reg-confirm-hint")
    confirm = value("confirm")
    ui.set_field_error("reg-confirm", "")
    if not confirm:
        hint.textContent = ""
    elif confirm == value("password"):
        hint.textContent = "Passwords match."
        hint.className = "field-hint ok"
    else:
        hint.textContent = "Passwords do not match yet."
        hint.className = "field-hint bad"


# --------------------------------------------------------------- submit
@when("submit", "#register-form")
def on_register_submit(event):
    event.preventDefault()
    ui.clear_alert("register-status")

    user, errors = auth.register(
        value("fullname"), value("email"), value("username"),
        value("password"), value("confirm"),
    )

    for field, input_id in FIELDS.items():
        ui.set_field_error(input_id, errors.get(field, ""))
    if errors:
        ui.show_alert("register-status", "Please fix the highlighted fields.", "error")
        return

    # Account created -> sign the new customer in and open their account page
    db.set_session(user["id"], False)
    ui.show_alert("register-status", "Account created! Taking you to your account...", "success")
    ui.el("register-submit").disabled = True
    ui.later(lambda: ui.go("account.html"), 800)
