import sqlite3
from flask import Flask, render_template, request, redirect, session, jsonify, flash, send_from_directory
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import login_required
import os

# AI citation: GitHub Copilot helped with Flask boilerplate structure and session configuration

app = Flask(__name__)
app.secret_key = "travelbd_secret_key_2026"

DATABASE = "travelbd.db"
LOGO_DIR = os.path.join(app.root_path, "logo")


def get_db():
    """Connect to the SQLite database and return a connection."""
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Create tables, seed once, and remove duplicate destination rows."""
    conn = get_db()
    schema_path = os.path.join(app.root_path, "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()

    seed_marker = "-- Seed the destinations table with our places"
    if seed_marker in schema_sql:
        create_sql, seed_sql = schema_sql.split(seed_marker, 1)
        conn.executescript(create_sql)

        dest_count = conn.execute("SELECT COUNT(*) AS c FROM destinations").fetchone()["c"]
        if dest_count == 0:
            conn.executescript(seed_marker + seed_sql)
    else:
        conn.executescript(schema_sql)

    extra_destinations = [
        ("Cox's Bazar", "Laboni Beach", "Golden sandy beach and one of the best sunset spots in Bangladesh", "laboni-beach-cox-bazar-sunset.jpg", 700),
        ("Sunamganj", "Tanguar Haor", "A serene wetland famous for boat rides and migratory birds", "traditional-baots-houseboat-tanguar-haor-sunamganj-famous-tourist-spot-bangladesh-was-raining-288058439.webp", 600),
        ("Khulna", "Sundarbans", "World heritage mangrove forest and home of the Royal Bengal Tiger", "sundarbans-mangrove-forest-bangladesh.jpg", 1200),
    ]

    for district, name, description, image, price in extra_destinations:
        exists = conn.execute(
            "SELECT 1 FROM destinations WHERE district = ? AND name = ?",
            (district, name),
        ).fetchone()
        if not exists:
            conn.execute(
                "INSERT INTO destinations (district, name, description, image, price) VALUES (?, ?, ?, ?, ?)",
                (district, name, description, image, price),
            )

    # Keep only one row per (district, name) if duplicates already exist.
    conn.execute("""
        DELETE FROM destinations
        WHERE id NOT IN (
            SELECT keep_id
            FROM (
                SELECT MIN(id) AS keep_id
                FROM destinations
                GROUP BY district, name
            )
        )
    """)
    conn.commit()
    conn.close()


@app.route("/logo/<path:filename>")
def serve_logo(filename):
    """Serve logo assets from the project logo folder."""
    return send_from_directory(LOGO_DIR, filename)


@app.route("/favicon.ico")
def favicon():
    """Serve favicon for browser tab icon."""
    return send_from_directory(LOGO_DIR, "travelbd.png")


@app.after_request
def after_request(response):
    """Make sure responses arent cached so we always get fresh data."""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/destinations")
def destinations():
    conn = get_db()
    # grab all destinations grouped by district
    rows = conn.execute("SELECT * FROM destinations ORDER BY district, name").fetchall()
    conn.close()

    # organize into a dict by district
    districts = {}
    for row in rows:
        d = row["district"]
        if d not in districts:
            districts[d] = []
        districts[d].append(dict(row))

    return render_template("destinations.html", districts=districts)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/bookticket")
def bookticket():
    return render_template("bookticket.html")


@app.route("/careers")
def careers():
    return render_template(
        "info_page.html",
        page_title="Careers",
        page_subtitle="Join the team behind memorable trips",
        page_heading="Build travel experiences with us",
        page_body="We welcome people who care about hospitality, local culture, and great service. Reach out through the contact page with your background and the role you are interested in.",
        highlights=[
            {"title": "Guides", "text": "Lead travelers with local knowledge and professional care."},
            {"title": "Operations", "text": "Help plan bookings, routes, and smooth guest experiences."},
            {"title": "Support", "text": "Assist travelers before and during their trips."},
        ],
        cta_text="Contact Us About Careers",
        cta_href="/contact",
    )


@app.route("/privacy-policy")
def privacy_policy():
    return render_template(
        "info_page.html",
        page_title="Privacy Policy",
        page_subtitle="How we handle your information",
        page_heading="Your data stays protected",
        page_body="We only use your details to manage bookings, respond to inquiries, and improve our services. We do not sell personal information to third parties.",
        highlights=[
            {"title": "Booking Data", "text": "Stored securely for reservation and support purposes."},
            {"title": "Contact Forms", "text": "Used only to respond to your request or message."},
            {"title": "Payments", "text": "Any payment details are handled through the booking workflow only."},
        ],
        cta_text="Go Back to Home",
        cta_href="/",
    )


@app.route("/terms")
def terms():
    return render_template(
        "info_page.html",
        page_title="Terms & Conditions",
        page_subtitle="Simple rules for a smooth trip",
        page_heading="Please review the booking terms",
        page_body="Bookings are subject to availability. Please provide accurate contact details, arrive on time, and review cancellation details before confirming a trip.",
        highlights=[
            {"title": "Accuracy", "text": "All booking details should be entered correctly before submission."},
            {"title": "Cancellation", "text": "Cancel early where possible so we can update your booking properly."},
            {"title": "Travel Conduct", "text": "Respect local rules, guides, and community spaces during tours."},
        ],
        cta_text="View Destinations",
        cta_href="/destinations",
    )


# ==================== SERVICE PAGES ====================

@app.route("/tour-planning")
def tour_planning():
    return render_template(
        "info_page.html",
        page_title="Tour Planning",
        page_subtitle="Customized itineraries for your perfect trip",
        page_heading="Let us plan your adventure",
        page_body="Our expert travel consultants work with you to create personalized tour itineraries. From budget backpacking to luxury getaways, we tailor every detail to your preferences.",
        highlights=[
            {"title": "Custom Itineraries", "text": "We design trips based on your interests, budget, and travel style."},
            {"title": "Local Expertise", "text": "Our team knows Bangladesh inside out and brings unique insights."},
            {"title": "24/7 Support", "text": "Dedicated support before, during, and after your journey."},
        ],
        cta_text="Start Planning Your Trip",
        cta_href="/contact",
    )


@app.route("/guide-services")
def guide_services():
    return render_template(
        "info_page.html",
        page_title="Guide Services",
        page_subtitle="Expert local guides for unforgettable experiences",
        page_heading="Travel with knowledgeable guides",
        page_body="Our professional guides are trained in multiple languages and have deep knowledge of Bangladesh's culture, history, and nature. They ensure safety, comfort, and authentic experiences.",
        highlights=[
            {"title": "Professional Guides", "text": "Certified professionals fluent in English and local languages."},
            {"title": "Small Groups", "text": "Personalized attention with groups limited to 15 people."},
            {"title": "Cultural Immersion", "text": "Learn from guides who share local traditions and stories."},
        ],
        cta_text="Book a Guide",
        cta_href="/bookticket",
    )


@app.route("/hotel-booking")
def hotel_booking():
    return render_template(
        "info_page.html",
        page_title="Hotel Booking",
        page_subtitle="Curated accommodations at the best rates",
        page_heading="Stay comfortably wherever you go",
        page_body="We partner with verified hotels, resorts, and guesthouses across Bangladesh. Get exclusive rates and guaranteed availability for your stay.",
        highlights=[
            {"title": "Best Rates Guaranteed", "text": "Price match guarantee on all hotel bookings."},
            {"title": "Wide Selection", "text": "From budget hostels to 5-star resorts across all districts."},
            {"title": "Free Cancellation", "text": "Flexible cancellation on most bookings up to 24 hours before check-in."},
        ],
        cta_text="Explore Hotels",
        cta_href="/contact",
    )


@app.route("/transportation")
def transportation():
    return render_template(
        "info_page.html",
        page_title="Transportation",
        page_subtitle="Reliable travel solutions across Bangladesh",
        page_heading="Hassle-free ground transport",
        page_body="We arrange all your transportation needs - airport pickups, intercity travel, and on-tour transportation. Our fleet includes cars, vans, and buses with experienced drivers.",
        highlights=[
            {"title": "Safe Vehicles", "text": "Well-maintained vehicles with trained drivers."},
            {"title": "Flexible Options", "text": "Private cars, shared transport, or group buses available."},
            {"title": "On-Time Service", "text": "Punctual pickups and drop-offs, always on schedule."},
        ],
        cta_text="Arrange Transport",
        cta_href="/contact",
    )


# ==================== ADMIN PANEL ====================
# Hardcoded admin credentials
ADMIN_EMAIL = "admin@travelbd.com"
ADMIN_PASSWORD = "admin123"


@app.route("/admin/logout")
def admin_logout():
    """Log out admin user."""
    session.pop("admin_id", None)
    session.pop("admin_email", None)
    flash("You have been logged out.", "success")
    return redirect("/")


def admin_required(f):
    """Decorator to check if user is logged in as admin."""
    def decorated_function(*args, **kwargs):
        if "admin_id" not in session:
            flash("Please log in as admin first.", "error")
            return redirect("/admin/login")
        return f(*args, **kwargs)
    decorated_function.__name__ = f.__name__
    return decorated_function


@app.route("/admin/dashboard")
@admin_required
def admin_dashboard():
    """Admin dashboard showing contacts and destination management."""
    conn = get_db()

    # Get all contacts
    contacts = conn.execute(
        "SELECT * FROM contacts ORDER BY created_at DESC"
    ).fetchall()

    # Get all destinations
    destinations = conn.execute(
        "SELECT * FROM destinations ORDER BY district, name"
    ).fetchall()

    # Get all registered users
    users = conn.execute(
        "SELECT id, name, email, created_at FROM users ORDER BY created_at DESC"
    ).fetchall()

    # Get booking stats
    guide_bookings_count = conn.execute("SELECT COUNT(*) as c FROM guide_bookings").fetchone()["c"]
    place_bookings_count = conn.execute("SELECT COUNT(*) as c FROM place_bookings").fetchone()["c"]
    total_users = len(users)

    conn.close()

    stats = {
        "total_contacts": len(contacts),
        "total_destinations": len(destinations),
        "guide_bookings": guide_bookings_count,
        "place_bookings": place_bookings_count,
        "total_users": total_users
    }

    return render_template(
        "admin_dashboard.html",
        contacts=contacts,
        destinations=destinations,
        users=users,
        stats=stats
    )


@app.route("/admin/contact/<int:contact_id>")
@admin_required
def admin_contact_detail(contact_id):
    """Show the full content of one contact message."""
    conn = get_db()
    contact = conn.execute(
        "SELECT * FROM contacts WHERE id = ?",
        (contact_id,)
    ).fetchone()
    conn.close()

    if contact is None:
        flash("Contact message not found.", "error")
        return redirect("/admin/dashboard")

    return render_template("admin_contact_detail.html", contact=contact)


@app.route("/admin/add-destination", methods=["POST"])
@admin_required
def admin_add_destination():
    """Add a new destination."""
    district = request.form.get("district", "").strip()
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    image = request.form.get("image", "").strip()
    price = request.form.get("price", 0)

    if not district or not name or not description or not image:
        flash("All fields are required.", "error")
        return redirect("/admin/dashboard")

    conn = get_db()
    conn.execute(
        "INSERT INTO destinations (district, name, description, image, price) VALUES (?, ?, ?, ?, ?)",
        (district, name, description, image, int(price))
    )
    conn.commit()
    conn.close()

    flash(f"Destination '{name}' added successfully!", "success")
    return redirect("/admin/dashboard")


@app.route("/admin/edit-destination/<int:destination_id>", methods=["POST"])
@admin_required
def admin_edit_destination(destination_id):
    """Edit an existing destination."""
    district = request.form.get("district", "").strip()
    name = request.form.get("name", "").strip()
    description = request.form.get("description", "").strip()
    image = request.form.get("image", "").strip()
    price = request.form.get("price", 0)

    if not district or not name or not description or not image:
        flash("All fields are required.", "error")
        return redirect("/admin/dashboard")

    conn = get_db()
    conn.execute(
        "UPDATE destinations SET district = ?, name = ?, description = ?, image = ?, price = ? WHERE id = ?",
        (district, name, description, image, int(price), destination_id)
    )
    conn.commit()
    conn.close()

    flash(f"Destination updated successfully!", "success")
    return redirect("/admin/dashboard")


@app.route("/admin/delete-destination/<int:destination_id>", methods=["POST"])
@admin_required
def admin_delete_destination(destination_id):
    """Delete a destination."""
    conn = get_db()

    # Get destination name for flash message
    dest = conn.execute("SELECT name FROM destinations WHERE id = ?", (destination_id,)).fetchone()
    if dest:
        # Delete any reviews linked to this destination
        conn.execute("DELETE FROM reviews WHERE destination_id = ?", (destination_id,))
        # Delete any favorites linked to this destination
        conn.execute("DELETE FROM favorites WHERE destination_id = ?", (destination_id,))
        # Delete the destination
        conn.execute("DELETE FROM destinations WHERE id = ?", (destination_id,))
        conn.commit()
        flash(f"Destination '{dest['name']}' deleted successfully!", "success")
    else:
        flash("Destination not found.", "error")

    conn.close()
    return redirect("/admin/dashboard")


@app.route("/admin/delete-contact/<int:contact_id>", methods=["POST"])
@admin_required
def admin_delete_contact(contact_id):
    """Delete a contact submission."""
    conn = get_db()
    conn.execute("DELETE FROM contacts WHERE id = ?", (contact_id,))
    conn.commit()
    conn.close()

    flash("Contact removed.", "success")
    return redirect("/admin/dashboard")


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not name or not email or not message:
            flash("Please fill in all required fields.", "error")
            return redirect("/contact")

        conn = get_db()
        conn.execute(
            "INSERT INTO contacts (name, email, phone, subject, message) VALUES (?, ?, ?, ?, ?)",
            (name, email, phone, subject, message)
        )
        conn.commit()
        conn.close()

        flash("Thank you for your message! We will get back to you soon.", "success")
        return redirect("/contact")

    return render_template("contact.html")


# ==================== AUTH ROUTES ====================

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirmation = request.form.get("confirmation", "")

        # validate all the fields
        if not name or len(name) < 2:
            flash("Name must be at least 2 characters.", "error")
            return redirect("/register")

        if not email or "@" not in email:
            flash("Please enter a valid email.", "error")
            return redirect("/register")

        if not password or len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect("/register")

        if password != confirmation:
            flash("Passwords do not match.", "error")
            return redirect("/register")

        conn = get_db()

        # check if email is already taken
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            conn.close()
            flash("An account with this email already exists.", "error")
            return redirect("/register")

        # hash the password and save
        hashed = generate_password_hash(password)
        conn.execute(
            "INSERT INTO users (name, email, hash) VALUES (?, ?, ?)",
            (name, email, hashed)
        )
        conn.commit()

        # auto login after registering
        user = conn.execute("SELECT id, name FROM users WHERE email = ?", (email,)).fetchone()
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]
        conn.close()

        flash(f"Welcome, {name}! Account created successfully.", "success")
        return redirect("/")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    # Preserve flash messages; only clear auth identity when entering login.
    session.pop("user_id", None)
    session.pop("user_name", None)
    session.pop("admin_id", None)
    session.pop("admin_email", None)

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")

        if not email or not password:
            flash("Please fill in all fields.", "error")
            return redirect("/login")

        if "@" not in email:
            flash("Please enter a valid email address.", "error")
            return redirect("/login")

        if len(password) < 6:
            flash("Password must be at least 6 characters.", "error")
            return redirect("/login")

        # Check if credentials match admin first
        if email == ADMIN_EMAIL.lower() and password == ADMIN_PASSWORD:
            session["admin_id"] = "admin"
            session["admin_email"] = email
            flash("Welcome Admin! You are now logged in.", "success")
            return redirect("/admin/dashboard")

        # Otherwise check regular users
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        conn.close()

        if not user or not check_password_hash(user["hash"], password):
            flash("Invalid email or password.", "error")
            return redirect("/login")

        # remember the user
        session["user_id"] = user["id"]
        session["user_name"] = user["name"]

        flash(f"Welcome back, {user['name']}!", "success")
        return redirect("/")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect("/")


# ==================== PROFILE ====================

@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session["user_id"],)).fetchone()

    if request.method == "POST":
        action = request.form.get("action")

        if action == "update_name":
            new_name = request.form.get("name", "").strip()
            if not new_name or len(new_name) < 2:
                flash("Name must be at least 2 characters.", "error")
            else:
                conn.execute("UPDATE users SET name = ? WHERE id = ?", (new_name, session["user_id"]))
                conn.commit()
                session["user_name"] = new_name
                flash("Name updated successfully!", "success")

        elif action == "change_password":
            current = request.form.get("current_password", "")
            new_pass = request.form.get("new_password", "")
            confirm = request.form.get("confirm_password", "")

            if not check_password_hash(user["hash"], current):
                flash("Current password is incorrect.", "error")
            elif len(new_pass) < 6:
                flash("New password must be at least 6 characters.", "error")
            elif new_pass != confirm:
                flash("New passwords do not match.", "error")
            else:
                new_hash = generate_password_hash(new_pass)
                conn.execute("UPDATE users SET hash = ? WHERE id = ?", (new_hash, session["user_id"]))
                conn.commit()
                flash("Password changed successfully!", "success")

        conn.close()
        return redirect("/profile")

    # get some stats for the profile page
    guide_count = conn.execute(
        "SELECT COUNT(*) as c FROM guide_bookings WHERE user_id = ?", (session["user_id"],)
    ).fetchone()["c"]
    place_count = conn.execute(
        "SELECT COUNT(*) as c FROM place_bookings WHERE user_id = ?", (session["user_id"],)
    ).fetchone()["c"]
    fav_count = conn.execute(
        "SELECT COUNT(*) as c FROM favorites WHERE user_id = ?", (session["user_id"],)
    ).fetchone()["c"]
    review_count = conn.execute(
        "SELECT COUNT(*) as c FROM reviews WHERE user_id = ?", (session["user_id"],)
    ).fetchone()["c"]
    conn.close()

    stats = {
        "guide_bookings": guide_count,
        "place_bookings": place_count,
        "favorites": fav_count,
        "reviews": review_count
    }

    return render_template("profile.html", user=user, stats=stats)


# ==================== BOOKINGS ====================

@app.route("/book-guide", methods=["POST"])
def book_guide():
    """Handle guide booking form - works with or without login."""
    name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    persons = request.form.get("persons", "")
    booking_date = request.form.get("date", "")
    duration = request.form.get("duration", "")
    message = request.form.get("message", "").strip()

    if not name or not phone or not persons or not booking_date:
        flash("Please fill in all required fields.", "error")
        return redirect("/")

    user_id = session.get("user_id")

    conn = get_db()
    conn.execute(
        "INSERT INTO guide_bookings (user_id, name, phone, persons, booking_date, duration, message) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, name, phone, int(persons), booking_date, int(duration) if duration else None, message)
    )
    conn.commit()
    conn.close()

    flash(f"Guide booking confirmed for {booking_date}! We will contact you at {phone}.", "success")
    return redirect("/")


@app.route("/book-place", methods=["POST"])
def book_place():
    """Handle place booking - submitted via AJAX from the modal."""
    data = request.get_json()
    if not data:
        return jsonify({"error": "No data received"}), 400

    name = data.get("name", "").strip()
    phone = data.get("phone", "").strip()
    booking_date = data.get("date", "")
    persons = data.get("persons", "")
    place_name = data.get("place_name", "")
    price = data.get("price", 0)

    if not name or not phone or not booking_date or not persons or not place_name:
        return jsonify({"error": "Please fill in all fields"}), 400

    user_id = session.get("user_id")

    conn = get_db()
    conn.execute(
        "INSERT INTO place_bookings (user_id, place_name, name, phone, booking_date, persons, price) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (user_id, place_name, name, phone, booking_date, int(persons), int(price))
    )
    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": f"Booking confirmed for {place_name}!"})


@app.route("/mybookings")
@login_required
def mybookings():
    conn = get_db()
    guide_bookings = conn.execute(
        "SELECT * FROM guide_bookings WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],)
    ).fetchall()
    place_bookings = conn.execute(
        "SELECT * FROM place_bookings WHERE user_id = ? ORDER BY created_at DESC",
        (session["user_id"],)
    ).fetchall()
    conn.close()

    return render_template("mybookings.html", guide_bookings=guide_bookings, place_bookings=place_bookings)


@app.route("/cancel-booking", methods=["POST"])
@login_required
def cancel_booking():
    booking_id = request.form.get("booking_id")
    booking_type = request.form.get("booking_type")

    if not booking_id or not booking_type:
        flash("Invalid request.", "error")
        return redirect("/mybookings")

    conn = get_db()

    if booking_type == "guide":
        # make sure this booking belongs to the current user
        booking = conn.execute(
            "SELECT id FROM guide_bookings WHERE id = ? AND user_id = ?",
            (booking_id, session["user_id"])
        ).fetchone()
        if booking:
            conn.execute("UPDATE guide_bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))
    elif booking_type == "place":
        booking = conn.execute(
            "SELECT id FROM place_bookings WHERE id = ? AND user_id = ?",
            (booking_id, session["user_id"])
        ).fetchone()
        if booking:
            conn.execute("UPDATE place_bookings SET status = 'cancelled' WHERE id = ?", (booking_id,))

    conn.commit()
    conn.close()

    flash("Booking cancelled successfully.", "success")
    return redirect("/mybookings")


# ==================== FAVORITES ====================

@app.route("/favorites")
@login_required
def favorites():
    conn = get_db()
    # AI citation: Copilot helped write this JOIN query
    favs = conn.execute("""
        SELECT d.*, f.id as fav_id, f.created_at as fav_date
        FROM favorites f
        JOIN destinations d ON f.destination_id = d.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    """, (session["user_id"],)).fetchall()
    conn.close()

    return render_template("favorites.html", favorites=favs)


@app.route("/toggle-favorite", methods=["POST"])
@login_required
def toggle_favorite():
    data = request.get_json()
    destination_id = data.get("destination_id")

    if not destination_id:
        return jsonify({"error": "Missing destination ID"}), 400

    conn = get_db()

    # check if already favorited
    existing = conn.execute(
        "SELECT id FROM favorites WHERE user_id = ? AND destination_id = ?",
        (session["user_id"], destination_id)
    ).fetchone()

    if existing:
        conn.execute("DELETE FROM favorites WHERE id = ?", (existing["id"],))
        conn.commit()
        conn.close()
        return jsonify({"favorited": False, "message": "Removed from favorites"})
    else:
        conn.execute(
            "INSERT INTO favorites (user_id, destination_id) VALUES (?, ?)",
            (session["user_id"], destination_id)
        )
        conn.commit()
        conn.close()
        return jsonify({"favorited": True, "message": "Added to favorites!"})


# ==================== REVIEWS ====================

@app.route("/add-review", methods=["POST"])
@login_required
def add_review():
    data = request.get_json()
    destination_id = data.get("destination_id")
    rating = data.get("rating")
    comment = data.get("comment", "").strip()

    if not destination_id or not rating:
        return jsonify({"error": "Rating and destination are required"}), 400

    if int(rating) < 1 or int(rating) > 5:
        return jsonify({"error": "Rating must be between 1 and 5"}), 400

    conn = get_db()

    # check if user already reviewed this destination
    existing = conn.execute(
        "SELECT id FROM reviews WHERE user_id = ? AND destination_id = ?",
        (session["user_id"], destination_id)
    ).fetchone()

    if existing:
        # update existing review
        conn.execute(
            "UPDATE reviews SET rating = ?, comment = ?, created_at = CURRENT_TIMESTAMP WHERE id = ?",
            (int(rating), comment, existing["id"])
        )
    else:
        conn.execute(
            "INSERT INTO reviews (user_id, destination_id, rating, comment) VALUES (?, ?, ?, ?)",
            (session["user_id"], destination_id, int(rating), comment)
        )

    conn.commit()
    conn.close()

    return jsonify({"success": True, "message": "Review submitted!"})


# ==================== API ENDPOINTS ====================

@app.route("/api/destinations")
def api_destinations():
    """Returns destination data as JSON for the frontend modals."""
    district = request.args.get("district", "")
    conn = get_db()

    if district:
        rows = conn.execute(
            "SELECT * FROM destinations WHERE district = ? ORDER BY name", (district,)
        ).fetchall()
    else:
        rows = conn.execute("SELECT * FROM destinations ORDER BY district, name").fetchall()

    # add average rating to each destination
    results = []
    for row in rows:
        d = dict(row)
        avg = conn.execute(
            "SELECT AVG(rating) as avg_rating, COUNT(*) as count FROM reviews WHERE destination_id = ?",
            (row["id"],)
        ).fetchone()
        d["avg_rating"] = round(avg["avg_rating"], 1) if avg["avg_rating"] else 0
        d["review_count"] = avg["count"]

        # check if current user has favorited this
        if session.get("user_id"):
            fav = conn.execute(
                "SELECT id FROM favorites WHERE user_id = ? AND destination_id = ?",
                (session["user_id"], row["id"])
            ).fetchone()
            d["is_favorited"] = fav is not None
        else:
            d["is_favorited"] = False

        results.append(d)

    conn.close()
    return jsonify(results)


@app.route("/api/search")
def api_search():
    """Search destinations by name or district using LIKE."""
    query = request.args.get("q", "").strip()
    if not query:
        return jsonify([])

    conn = get_db()
    rows = conn.execute(
        "SELECT * FROM destinations WHERE name LIKE ? OR district LIKE ? ORDER BY district, name",
        (f"%{query}%", f"%{query}%")
    ).fetchall()
    conn.close()

    return jsonify([dict(row) for row in rows])


@app.route("/api/reviews/<int:destination_id>")
def api_reviews(destination_id):
    """Get all reviews for a destination."""
    conn = get_db()
    reviews = conn.execute("""
        SELECT r.*, u.name as user_name
        FROM reviews r
        JOIN users u ON r.user_id = u.id
        WHERE r.destination_id = ?
        ORDER BY r.created_at DESC
    """, (destination_id,)).fetchall()
    conn.close()

    return jsonify([dict(r) for r in reviews])


@app.route("/api/featured")
def api_featured():
    """Get featured destinations with highest ratings."""
    conn = get_db()
    rows = conn.execute("""
        SELECT d.*, COALESCE(AVG(r.rating), 0) as avg_rating, COUNT(r.id) as review_count
        FROM destinations d
        LEFT JOIN reviews r ON d.id = r.destination_id
        GROUP BY d.id
        ORDER BY avg_rating DESC, review_count DESC
        LIMIT 6
    """).fetchall()
    conn.close()

    results = []
    for row in rows:
        d = dict(row)
        if session.get("user_id"):
            fav = conn.execute(
                "SELECT id FROM favorites WHERE user_id = ? AND destination_id = ?",
                (session["user_id"], row["id"])
            ).fetchone()
            d["is_favorited"] = fav is not None
        else:
            d["is_favorited"] = False
        results.append(d)

    return jsonify(results)


# Initialize database on module import so WSGI servers (e.g. Gunicorn) also run setup.
init_db()


if __name__ == "__main__":
    app.run(debug=True, port=5000)
