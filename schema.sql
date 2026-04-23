-- TravelBangladesh Database Schema
-- Sets up all the tables we need for the app

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    hash TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS destinations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    district TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT,
    image TEXT,
    price INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS guide_bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    persons INTEGER NOT NULL,
    booking_date TEXT NOT NULL,
    duration INTEGER,
    message TEXT,
    status TEXT DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS place_bookings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    place_name TEXT NOT NULL,
    name TEXT NOT NULL,
    phone TEXT NOT NULL,
    booking_date TEXT NOT NULL,
    persons INTEGER NOT NULL,
    price INTEGER,
    status TEXT DEFAULT 'confirmed',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS reviews (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
    comment TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (destination_id) REFERENCES destinations(id)
);

CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    destination_id INTEGER NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (destination_id) REFERENCES destinations(id),
    UNIQUE(user_id, destination_id)
);

CREATE TABLE IF NOT EXISTS contacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone TEXT,
    subject TEXT,
    message TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed the destinations table with our places
INSERT INTO destinations (district, name, description, image, price) VALUES
('Dhaka', 'Lalbagh Fort', 'Historic Mughal fort built in the 17th century', 'lalbagh-fort-dhaka-historical-monument.jpg', 500),
('Dhaka', 'Ahsan Manzil', 'The Pink Palace - Former residential palace and seat of the Nawab of Dhaka', 'ahsan-manzil-pink-palace-dhaka.jpg', 300),
('Dhaka', 'National Parliament House', 'Iconic architecture by Louis Kahn', 'national-parliament-house-bangladesh-architecture.jpg', 200),
('Dhaka', 'Sadarghat River Port', 'One of the largest river ports in the world', 'beautiful-bangladesh-landscape-with-rivers-and-gre.jpg', 100),
('Chittagong', 'Patenga Beach', 'Popular beach near the city with beautiful sunset views', 'patenga-beach-chittagong-sunset.jpg', 50),
('Chittagong', 'Foys Lake', 'Scenic man-made lake with amusement park', 'foys-lake-chittagong-amusement-park.jpg', 200),
('Chittagong', 'Ethnological Museum', 'Museum showcasing Bangladeshs tribal heritage', 'ethnological-museum-chittagong.jpg', 150),
('Chittagong', 'Bhatiary Lakes', 'Beautiful natural lakes surrounded by hills', 'hatirjheel-dhaka-waterfront-night-lights.jpg', 100),
('Sylhet', 'Ratargul Swamp Forest', 'Only swamp forest in Bangladesh', 'ratargul-swamp-forest-sylhet-boat.jpg', 800),
('Sylhet', 'Jaflong', 'Stone collection area with crystal clear water', 'jaflong-sylhet-stone-collection-river.jpg', 1000),
('Sylhet', 'Tea Gardens', 'Beautiful tea estates with green hills', 'srimangal-tea-garden-bangladesh.jpg', 500),
('Sylhet', 'Sreemangal', 'Tea capital of Bangladesh with lush greenery', 'srimangal-tea-garden-bangladesh-green.jpg', 600);
