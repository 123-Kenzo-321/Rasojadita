"""Landing page events: product search, request buttons, gallery lightbox,
student-discount shortcut and the custom commission message box."""
from pyscript import document, when
from pyscript.ffi import create_proxy

import auth
import db
import ui

user = ui.init_page()

MAX_MESSAGE = 500


# ----------------------------------------------------------- product search
def run_search(scroll=False):
    query = ui.el("search-input").value.strip().lower()
    shown = 0
    total = 0
    for card in document.querySelectorAll(".product-card"):
        total += 1
        haystack = (card.getAttribute("data-keywords") or "").lower()
        if not query or query in haystack:
            card.classList.remove("hidden")
            shown += 1
        else:
            card.classList.add("hidden")

    summary = ui.el("search-summary")
    if query and shown:
        summary.textContent = f'Showing {shown} of {total} products for "{query}".'
    else:
        summary.textContent = ""
    if shown == 0 and query:
        ui.show("no-results")
        ui.el("no-results-query").textContent = query
    else:
        ui.hide("no-results")
    if scroll:
        ui.el("products").scrollIntoView()


@when("click", "#search-btn")
def on_search_click(event):
    run_search(scroll=True)


@when("input", "#search-input")
def on_search_input(event):
    run_search(scroll=False)


@when("keydown", "#search-input")
def on_search_key(event):
    if event.key == "Enter":
        run_search(scroll=True)


@when("click", ".search-chip")
def on_chip_click(event):
    ui.el("search-input").value = event.currentTarget.getAttribute("data-query")
    run_search(scroll=True)


@when("click", "#clear-search")
def on_clear_search(event):
    ui.el("search-input").value = ""
    run_search(scroll=False)


# ------------------------------------------- "Request this" + student CTA
def focus_request_form():
    ui.el("custom-request").scrollIntoView()
    ui.el("cr-message").focus()


@when("click", ".request-btn")
def on_request_click(event):
    ui.el("cr-product").value = event.currentTarget.getAttribute("data-product")
    focus_request_form()


@when("click", "#student-cta")
def on_student_cta(event):
    ui.el("cr-student").checked = True
    focus_request_form()


# ------------------------------------------------------------ gallery
def close_lightbox():
    ui.hide("lightbox")


@when("click", ".gallery-item")
def on_gallery_click(event):
    item = event.currentTarget
    ui.el("lightbox-img").src = item.getAttribute("data-src")
    ui.el("lightbox-img").alt = item.getAttribute("data-caption")
    ui.el("lightbox-caption").textContent = item.getAttribute("data-caption")
    ui.show("lightbox")


@when("click", "#lightbox")
def on_lightbox_click(event):
    # close when the dark backdrop or the X is clicked, not the picture itself
    if event.target.tagName != "IMG":
        close_lightbox()


def on_keydown(event):
    if event.key == "Escape":
        close_lightbox()


document.addEventListener("keydown", create_proxy(on_keydown))


# -------------------------------------------------- custom commission box
def prefill_form():
    if user:
        ui.el("cr-name").value = user["fullname"]
        ui.el("cr-email").value = user["email"]


@when("input", "#cr-message")
def on_message_input(event):
    length = len(ui.el("cr-message").value)
    counter = ui.el("cr-counter")
    counter.textContent = f"{length}/{MAX_MESSAGE}"
    if length > MAX_MESSAGE:
        counter.classList.add("text-red-600")
    else:
        counter.classList.remove("text-red-600")


@when("submit", "#commission-form")
def on_commission_submit(event):
    event.preventDefault()
    ui.clear_alert("cr-status")

    name = auth.clean_name(ui.el("cr-name").value)
    email = ui.el("cr-email").value.strip()
    product = ui.el("cr-product").value
    text = ui.el("cr-message").value.strip()
    is_student = ui.el("cr-student").checked

    errors = {}
    if len(name) < 2:
        errors["cr-name"] = "Please enter your name."
    if not auth.EMAIL_RE.match(email):
        errors["cr-email"] = "Enter a valid email so the artist can reply."
    if not product:
        errors["cr-product"] = "Choose what you would like drawn."
    if len(text) < 10:
        errors["cr-message"] = "Please describe your request (at least 10 characters)."
    elif len(text) > MAX_MESSAGE:
        errors["cr-message"] = f"Message is too long ({MAX_MESSAGE} characters max)."

    for field in ("cr-name", "cr-email", "cr-product", "cr-message"):
        ui.set_field_error(field, errors.get(field, ""))
    if errors:
        return

    db.add_message(user["id"] if user else None, name, email, product, is_student, text)
    ui.show_alert(
        "cr-status",
        "Request sent! The artist will reply through Messenger or email "
        "to agree on details, price and your 50% down payment.",
        "success",
    )
    ui.el("commission-form").reset()
    ui.el("cr-counter").textContent = f"0/{MAX_MESSAGE}"
    prefill_form()


prefill_form()
