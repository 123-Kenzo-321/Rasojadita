"""Login page events: submit, show/hide password."""
from pyscript import when

import auth
import ui

if ui.init_page():
    # already signed in -> go straight to the account page
    ui.go("account.html")


@when("click", ".toggle-pw")
def on_toggle_password(event):
    target = ui.el(event.currentTarget.getAttribute("data-target"))
    showing = target.type == "text"
    target.type = "password" if showing else "text"
    event.currentTarget.textContent = "Show" if showing else "Hide"


@when("submit", "#login-form")
def on_login_submit(event):
    event.preventDefault()
    ui.clear_alert("login-error")

    identifier = ui.el("login-identifier").value
    password = ui.el("login-password").value
    remember = ui.el("login-remember").checked

    user, error = auth.login(identifier, password, remember)
    if error:
        ui.show_alert("login-error", error, "error")
        ui.el("login-password").value = ""
        return

    ui.show_alert("login-error", "Welcome back! Redirecting...", "success")
    ui.el("login-submit").disabled = True
    ui.later(lambda: ui.go("account.html"), 600)
