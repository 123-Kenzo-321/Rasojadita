"""Account page: profile, logout, customer requests, admin inbox + user list."""
from pyscript import when

import auth
import db
import ui

user = ui.init_page()
if not user:
    ui.go("login.html")


def render_profile():
    ui.el("acc-welcome").textContent = user["fullname"].split(" ")[0]
    ui.el("acc-fullname").textContent = user["fullname"]
    ui.el("acc-username").textContent = user["username"]
    ui.el("acc-email").textContent = user["email"]
    ui.el("acc-since").textContent = ui.format_time(user["created_at"])
    role = ui.el("acc-role")
    role.textContent = "Artist / Admin" if user["role"] == "admin" else "Customer"
    role.className = "badge " + ("badge-admin" if user["role"] == "admin" else "badge-customer")


def status_badge(status):
    return '<span class="badge badge-' + ui.esc(status) + '">' + ui.esc(status.upper()) + "</span>"


def render_customer():
    ui.show("customer-panel")
    mine = [
        m for m in db.get_messages()
        if m["user_id"] == user["id"] or m["email"] == user["email"].lower()
    ]
    box = ui.el("my-requests")
    if not mine:
        box.innerHTML = '<p class="text-sm text-slate-500">You have not sent any commission requests yet.</p>'
        return
    rows = []
    for m in reversed(mine):
        rows.append(
            '<div class="border border-violet-100 rounded-xl p-3 mb-2">'
            '<div class="flex justify-between items-center gap-2 mb-1">'
            '<strong class="text-violet-800">' + ui.esc(m["product"]) + "</strong>"
            + status_badge(m["status"]) + "</div>"
            '<p class="text-sm text-slate-700">' + ui.esc(m["text"]) + "</p>"
            '<p class="text-xs text-slate-400 mt-1">' + ui.esc(ui.format_time(m["created_at"])) + "</p>"
            "</div>"
        )
    box.innerHTML = "".join(rows)


def render_admin():
    ui.show("admin-panel")

    users = db.get_users()
    ui.el("stat-users").textContent = str(len(users))
    messages = db.get_messages()
    ui.el("stat-messages").textContent = str(len(messages))
    ui.el("stat-new").textContent = str(len([m for m in messages if m["status"] == "new"]))

    body = []
    for u in users:
        body.append(
            "<tr><td>" + ui.esc(u["fullname"]) + "</td><td>" + ui.esc(u["username"])
            + "</td><td>" + ui.esc(u["email"]) + "</td><td>" + ui.esc(u["role"]) + "</td></tr>"
        )
    ui.el("users-body").innerHTML = "".join(body)

    box = ui.el("messages-list")
    if not messages:
        box.innerHTML = '<p class="text-sm text-slate-500">No commission requests yet.</p>'
        return
    cards = []
    for m in reversed(messages):
        student = ' <span class="badge badge-customer">STUDENT</span>' if m["is_student"] else ""
        done_label = "Reopen" if m["status"] == "done" else "Mark done"
        cards.append(
            '<div class="border border-violet-100 rounded-xl p-3 mb-3">'
            '<div class="flex flex-wrap justify-between items-center gap-2 mb-1">'
            "<strong class=\"text-violet-800\">" + ui.esc(m["product"]) + "</strong>"
            "<span>" + status_badge(m["status"]) + student + "</span></div>"
            '<p class="text-sm text-slate-700">' + ui.esc(m["text"]) + "</p>"
            '<p class="text-xs text-slate-500 mt-1">From ' + ui.esc(m["name"]) + " &lt;" + ui.esc(m["email"])
            + "&gt; &middot; " + ui.esc(ui.format_time(m["created_at"])) + "</p>"
            '<div class="mt-2 flex gap-2">'
            '<button type="button" class="done-msg btn-ghost px-3 py-1 text-xs" data-id="' + str(m["id"]) + '">'
            + done_label + "</button>"
            '<button type="button" class="delete-msg btn-ghost px-3 py-1 text-xs" data-id="' + str(m["id"]) + '">'
            "Delete</button></div></div>"
        )
    box.innerHTML = "".join(cards)


# The inbox is redrawn often, so one listener on the container handles all
# of its buttons (event delegation).
@when("click", "#messages-list")
def on_inbox_click(event):
    done = event.target.closest(".done-msg")
    delete = event.target.closest(".delete-msg")
    if done:
        message_id = int(done.getAttribute("data-id"))
        current = [m for m in db.get_messages() if m["id"] == message_id]
        if current:
            db.set_message_status(message_id, "new" if current[0]["status"] == "done" else "done")
    elif delete:
        db.delete_message(int(delete.getAttribute("data-id")))
    else:
        return
    render_admin()


@when("click", "#logout-main")
def on_logout_click(event):
    auth.logout()
    ui.go("index.html")


if user:
    render_profile()
    if user["role"] == "admin":
        render_admin()
    else:
        render_customer()
