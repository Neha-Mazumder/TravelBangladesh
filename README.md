# TravelBangladesh

#### Video Demo: https://youtu.be/9y3znW_Lqyw

#### Description:

TravelBangladesh is my CS50x final project. It's a full-stack travel web application built with Flask, SQLite, HTML/CSS, and vanilla JavaScript. The idea came from a simple frustration — planning a trip inside Bangladesh usually means jumping between five different websites just to figure out where to go, how much it costs, and how to book something. I wanted to build one place that handles all of that.

I picked this project because I wanted to build something real, not just a demo. Bangladesh has genuinely beautiful places that most people outside the country don't know about, and even locals don't always have easy access to organized trip planning. This app tries to fix that in a small way.

The stack follows what I learned in CS50. Flask handles routing, sessions, and server-side logic. SQLite is the database because it's lightweight and needs zero setup. Jinja2 templates handle the server-rendered HTML, and vanilla JavaScript handles the interactive parts — modals, AJAX calls, search, filtering, and favorites toggling. I deliberately avoided frontend frameworks and ORMs so I could stay close to the fundamentals the course teaches.

---

## Features

**Destination exploration**
- Browse destinations organized by district
- Search by place name or district with debounced live results
- Filter by price range and sort by name or price

**Booking**
- Guide booking form (standard POST, works without login)
- Place booking through a modal using AJAX — no page reload
- Logged-in users can view all their bookings and cancel them

**Authentication**
- Register, login, logout
- Passwords stored as hashed values using Werkzeug
- After registering, users are automatically logged in
- Admin login goes through the same `/login` route — no separate page needed

**Reviews and favorites**
- Logged-in users can leave 1–5 star ratings with optional comments
- Submitting a second review updates the existing one instead of duplicating
- Favorite button on every place card — toggles instantly via AJAX
- Favorites page shows all saved places with remove and book options

**Contact and admin**
- Contact form saves messages to the database
- Admin dashboard shows registered users, all contact submissions, and destination management
- Admin can add or delete destinations, and view or delete contact messages

---

## File Structure

### app.py
The main Flask application. Everything routes through here — public pages, auth, bookings, favorites, reviews, admin panel, and JSON API endpoints. `init_db()` runs on startup to create tables, seed destinations once, and clean up any duplicate rows. Parameterized queries are used throughout to avoid SQL injection.

### helpers.py
Contains the `login_required` decorator. Borrowed the pattern from CS50 Finance and adapted it here. Keeps route protection clean and reusable without repeating session checks everywhere.

### schema.sql
Defines all seven tables: `users`, `destinations`, `guide_bookings`, `place_bookings`, `reviews`, `favorites`, and `contacts`. Also contains the initial seed data for destinations. The schema uses `IF NOT EXISTS` so it's safe to run on every startup.

### templates/layout.html
The base template that every page extends. Holds the navbar (with dynamic login/admin state), flash message rendering, all three shared modals (district places, place booking, review), and the footer. Keeping shared structure here means individual page templates only need to worry about their own content.

### templates/index.html
Homepage. Has the hero section, stats, district cards, featured destinations, Tanguar Haor section, testimonials, guide booking form, newsletter, and "Our Strength" section.

### templates/destinations.html
The main exploration page. Includes the search bar, price filter, sort dropdown, and district cards that open the places modal.

### templates/bookticket.html
Focused on the Tanguar Haor houseboat experience and three popular tour packages, each with a direct booking button.

### templates/contact.html
Contact info cards and a form that saves submissions to the database.

### templates/login.html / register.html
Auth forms with client-side validation hints and server-side validation in the route.

### templates/profile.html
Shows booking counts, favorites count, and review count. Lets users update their name or change their password.

### templates/mybookings.html
Lists all guide and place bookings for the logged-in user, with cancel buttons for confirmed ones.

### templates/favorites.html
Shows all favorited destinations with book and remove options.

### templates/admin_dashboard.html
Admin-only page. Shows platform stats, registered users table, contact submissions table, and destination add/delete tools.

### templates/admin_contact_detail.html
Full view of a single contact message, with a delete button.

### templates/info_page.html
Reusable template used for service pages (Tour Planning, Guide Services, Hotel Booking, Transportation) and policy pages (Privacy Policy, Terms, Careers). Takes title, subtitle, body text, highlights, and a CTA link as template variables.

### static/style.css
All custom CSS. Dark theme with green and gold accents. Covers layout, cards, modals, forms, flash messages, auth pages, profile, bookings, favorites, star ratings, search, filters, and responsive breakpoints.

### static/script.js
All client-side JavaScript. Handles modal open/close, district places fetch, place booking AJAX, favorites toggle, review modal and submission, debounced search, flash message auto-dismiss, newsletter form, and destination page filter/sort logic.

---

## Design Decisions

**AJAX vs. classic form submission** — I used standard POST redirects for login, register, guide booking, and contact because they're simple and don't need to stay on the same page. For place booking and reviews I used AJAX because they happen inside modals — a full page reload would close the modal and break the flow.

**Admin through the same login route** — Rather than building a separate admin login page and session flow, admin credentials are checked first inside the regular `/login` route. If they match, an `admin_id` session key is set instead of `user_id`. This kept the auth logic in one place and made it easier to maintain.

**Lightweight stack** — No React, no SQLAlchemy, no external auth libraries. Just Flask, SQLite, Jinja2, and vanilla JS. This was intentional — I wanted to understand every layer of what the app is doing, which is exactly what CS50 pushes you toward.

**Duplicate cleanup on startup** — `init_db()` runs a DELETE query on startup to remove any duplicate destination rows. This was added after I noticed the seed data was being inserted multiple times during development restarts.

---

## Security Notes

- Passwords are hashed with Werkzeug's `generate_password_hash` / `check_password_hash`
- All SQL queries use parameterized placeholders — no string formatting into queries
- Session checks protect all user-only and admin-only routes
- Server-side validation runs on all form inputs before anything touches the database

---

## How to Run

1. Open a terminal inside the project folder.

2. Create and activate a virtual environment (recommended):
   ```
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Run the app:
   ```
   python app.py
   ```

5. Open your browser at:
   ```
   http://127.0.0.1:5000
   ```

The database is created and seeded automatically on first run. No manual setup needed.

---

## Admin Access

Admin login uses the normal `/login` page.

- Email: `admin@travelbd.com`
- Password: `admin123`

These are hardcoded for demo/project purposes.

---

## AI Usage Disclosure

I used GitHub Copilot as a coding assistant during development. The files where it helped are marked with a comment at the top of the file. In every case I reviewed what it suggested, understood it, and integrated it into my own logic. The overall architecture, feature decisions, and final implementation are my own work.

