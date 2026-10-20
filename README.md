# Rasojadita Art Commissions - Website (Stage 1)

Event-Driven Programming final project, BSIT-3 Section 11. A PyScript business website for **Rasojadita Art Commissions** (hand-drawn physical artwork, Cebu City).

**Stage 1 includes:** landing page, register, login, and a My Account page, all backed by a local (browser) database.

## Run it locally

PyScript must load its Python files over HTTP, so do not double-click `index.html`. From this folder run:

```
python -m http.server 8000
```' 

Then open <http://localhost:8000>. An internet connection is needed (Tailwind, PyScript and the font load from CDNs). The first load takes a few seconds while PyScript starts.

## Publish on GitHub Pages

Push the folder to a public repo, then Settings > Pages > Deploy from branch (`main`, `/root`). The site is fully static, so no server is needed.

## Demo accounts

| Role | Username | Password |
|------|----------|----------|
| Artist / Admin (seeded) | `admin` | `Admin@123` |
| Customer | register your own | |

The admin account sees the commission-request inbox (mark done / delete) and the list of registered users. Customers see their own requests.

## How the local database works

`py/db.py` stores JSON in the browser's `localStorage` through PyScript (tables: `users`, `messages`; the login session lives in `sessionStorage`, or `localStorage` when "Remember me" is ticked). Data exists only in the browser that created it. To reset: DevTools > Application > Storage > Clear site data.

Passwords are salted and hashed before storing, but this is a client-side demo, not production security.

## Project structure

```
index.html  login.html  register.html  account.html   pages
pyscript.toml                                          loads the .py modules
css/style.css                                          shared styles
assets/logo.svg                                        purple cat logo
assets/gallery/sample-*.svg                            placeholder sample works
py/db.py        local database (localStorage)
py/auth.py      register / login / session / validation (no DOM code)
py/ui.py        shared DOM helpers and navigation
py/landing.py   search, request buttons, gallery lightbox, commission form
py/login.py     login events
py/register.py  live validation, password strength, register
py/account.py   profile, customer requests, admin inbox
tests/test_logic.py   run: python tests/test_logic.py
```


