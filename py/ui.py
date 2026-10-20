"""Shared DOM helpers used by every page (browser only)."""
import html

from pyscript import document, window
from pyscript.ffi import create_proxy

import auth


# ------------------------------------------------------------ DOM helpers
def el(element_id):
    return document.getElementById(element_id)


def show(element_id):
    el(element_id).classList.remove("hidden")


def hide(element_id):
    el(element_id).classList.add("hidden")


def esc(value):
    """Escape user-provided text before putting it inside innerHTML."""
    return html.escape(str(value), quote=True)


def format_time(timestamp):
    """Format an epoch timestamp in the visitor's local time zone."""
    try:
        return str(window.Date.new(timestamp * 1000).toLocaleString())
    except Exception:
        return str(timestamp)


def go(url):
    window.location.href = url


def later(callback, ms):
    window.setTimeout(create_proxy(callback), ms)


# ------------------------------------------------------- form feedback
def set_field_error(input_id, message):
    """Show (or clear) the red error text under a field."""
    field = el(input_id)
    error = el(input_id + "-error")
    if message:
        field.classList.add("field-invalid")
        error.textContent = message
    else:
        field.classList.remove("field-invalid")
        error.textContent = ""


def show_alert(box_id, message, kind="error"):
    box = el(box_id)
    box.className = "alert alert-" + kind + " fade-in"
    box.textContent = message


def clear_alert(box_id):
    box = el(box_id)
    box.className = "hidden"
    box.textContent = ""


# ------------------------------------------------------------ navigation
def _on_logout(event):
    auth.logout()
    go("index.html")


def render_nav():
    """Swap Login/Sign Up for My Account/Logout depending on the session."""
    user = auth.current_user()
    if user:
        first_name = esc(user["fullname"].split(" ")[0])
        desktop = (
            '<a href="account.html" class="nav-link">Hi, ' + first_name + '</a>'
            '<button type="button" class="js-logout btn-outline-light px-4 py-1.5 text-sm">Logout</button>'
        )
        mobile = (
            '<a href="account.html" class="nav-link-dark py-1">My Account (' + first_name + ')</a>'
            '<button type="button" class="js-logout btn-ghost px-4 py-1.5 text-sm text-left">Logout</button>'
        )
    else:
        desktop = (
            '<a href="login.html" class="nav-link">Login</a>'
            '<a href="register.html" class="btn-glow px-5 py-2 text-sm">Sign Up</a>'
        )
        mobile = (
            '<a href="login.html" class="nav-link-dark py-1">Login</a>'
            '<a href="register.html" class="nav-link-dark py-1">Sign Up</a>'
        )
    el("nav-auth").innerHTML = desktop
    el("mobile-auth").innerHTML = mobile
    for button in document.querySelectorAll(".js-logout"):
        button.addEventListener("click", create_proxy(_on_logout))
    return user


def init_page():
    """Common start-up for every page: seed data, draw nav, hide loader."""
    auth.ensure_seed_admin()
    user = render_nav()
    loader = document.getElementById("app-loading")
    if loader:
        loader.classList.add("hidden")
    year = document.getElementById("year")
    if year:
        year.textContent = str(window.Date.new().getFullYear())
    return user
