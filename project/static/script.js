// TravelBangladesh - Client-side JavaScript
// Handles modals, booking forms, search, favorites, and reviews
// AI citation: GitHub Copilot helped structure the fetch API calls used throughout this file

// ==================== MODAL FUNCTIONS ====================

function closeModal(modalId) {
    var modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
}

function openModal(modalId) {
    var modal = document.getElementById(modalId);
    if (modal) {
        modal.style.display = 'flex';
        document.body.style.overflow = 'hidden';
    }
}

// close modal when clicking outside it
window.addEventListener('click', function(e) {
    if (e.target.classList.contains('modal')) {
        e.target.style.display = 'none';
        document.body.style.overflow = 'auto';
    }
});


// ==================== DISTRICT PLACES ====================

function showDistrictPlaces(district) {
    var modal = document.getElementById('districtPlacesModal');
    var title = document.getElementById('districtModalTitle');
    var container = document.getElementById('placesContainer');

    title.textContent = district;
    container.innerHTML = '<p style="text-align:center;color:rgba(255,255,255,0.5);">Loading...</p>';
    openModal('districtPlacesModal');

    // fetch from our Flask API
    fetch('/api/destinations?district=' + encodeURIComponent(district))
        .then(function(res) { return res.json(); })
        .then(function(places) {
            container.innerHTML = '';

            places.forEach(function(place) {
                var card = document.createElement('div');
                card.className = 'place-card';

                var starsHtml = '';
                if (place.avg_rating > 0) {
                    starsHtml = '<div class="avg-rating"><i class="fa-solid fa-star"></i> ' + place.avg_rating + '/5 (' + place.review_count + ' reviews)</div>';
                }

                var favClass = place.is_favorited ? 'active' : '';
                var favIcon = place.is_favorited
                    ? '<i class="fa-solid fa-heart"></i>'
                    : '<i class="fa-regular fa-heart"></i>';

                card.innerHTML = ''
                    + '<img src="/static/image/' + place.image + '" alt="' + place.name + '">'
                    + '<div class="place-info">'
                    + '  <h3>' + place.name + '</h3>'
                    + '  <p>' + place.description + '</p>'
                    + '  <p class="place-price">Entry Fee: ' + place.price + ' BDT</p>'
                    + starsHtml
                    + '  <div class="place-card-actions">'
                    + '    <button class="book-place-btn" onclick="bookPlace(\'' + place.name.replace(/'/g, "\\'") + '\', ' + place.price + ')">Book Now</button>'
                    + '    <button class="fav-btn ' + favClass + '" onclick="toggleFavorite(' + place.id + ', this)" title="Favorite">' + favIcon + '</button>'
                    + '    <button class="review-btn" onclick="openReviewModal(' + place.id + ', \'' + place.name.replace(/'/g, "\\'") + '\')" title="Review"><i class="fa-regular fa-pen-to-square"></i></button>'
                    + '  </div>'
                    + '</div>';

                container.appendChild(card);
            });
        })
        .catch(function(err) {
            container.innerHTML = '<p style="text-align:center;color:red;">Failed to load places.</p>';
        });
}


// ==================== BOOK PLACE ====================

function bookPlace(placeName, price) {
    closeModal('districtPlacesModal');

    document.getElementById('bookPlaceName').textContent = placeName;
    document.getElementById('bookPlacePrice').textContent = price;

    // auto-fill name if logged in so user doesn't have to type it again
    if (IS_LOGGED_IN && USER_NAME) {
        document.getElementById('placeBookingName').value = USER_NAME;
    }

    openModal('bookPlaceModal');
}


// ==================== FAVORITES ====================

function toggleFavorite(destId, btn) {
    if (!IS_LOGGED_IN) {
        alert('Please login to save favorites.');
        window.location.href = '/login';
        return;
    }

    fetch('/toggle-favorite', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ destination_id: destId })
    })
    .then(function(res) { return res.json(); })
    .then(function(data) {
        if (data.favorited) {
            btn.innerHTML = '<i class="fa-solid fa-heart"></i>';
            btn.classList.add('active');
        } else {
            btn.innerHTML = '<i class="fa-regular fa-heart"></i>';
            btn.classList.remove('active');
            // if we're on the favorites page, remove the card
            if (window.location.pathname === '/favorites') {
                var card = btn.closest('.place-card');
                if (card) card.remove();
            }
        }
    })
    .catch(function() {
        alert('Something went wrong.');
    });
}


// ==================== REVIEWS ====================

function openReviewModal(destId, placeName) {
    if (!IS_LOGGED_IN) {
        alert('Please login to write a review.');
        window.location.href = '/login';
        return;
    }

    document.getElementById('reviewDestId').value = destId;
    document.getElementById('reviewPlaceName').textContent = placeName;
    document.getElementById('reviewRating').value = 0;
    document.getElementById('reviewComment').value = '';

    // reset stars
    document.querySelectorAll('#reviewForm .star').forEach(function(s) {
        s.classList.remove('active');
    });

    closeModal('districtPlacesModal');
    openModal('reviewModal');
}


// ==================== SEARCH ====================

var searchTimer = null;

function setupSearch() {
    var input = document.getElementById('searchInput');
    var results = document.getElementById('searchResults');

    if (!input || !results) return;

    input.addEventListener('input', function() {
        clearTimeout(searchTimer);
        var query = input.value.trim();

        if (query.length < 2) {
            results.style.display = 'none';
            return;
        }

        // debounce the search so we dont spam the server
        searchTimer = setTimeout(function() {
            fetch('/api/search?q=' + encodeURIComponent(query))
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    results.innerHTML = '';
                    if (data.length === 0) {
                        results.innerHTML = '<div class="search-result-item"><span class="result-name">No results found</span></div>';
                    } else {
                        data.forEach(function(d) {
                            var item = document.createElement('div');
                            item.className = 'search-result-item';
                            item.innerHTML = '<span class="result-name">' + d.name + '</span><br><span class="result-district">' + d.district + ' · ' + d.price + ' BDT</span>';
                            item.onclick = function() {
                                showDistrictPlaces(d.district);
                                results.style.display = 'none';
                                input.value = '';
                            };
                            results.appendChild(item);
                        });
                    }
                    results.style.display = 'block';
                });
        }, 300);
    });

    // hide results when clicking away
    document.addEventListener('click', function(e) {
        if (!input.contains(e.target) && !results.contains(e.target)) {
            results.style.display = 'none';
        }
    });
}


// ==================== INIT ====================

document.addEventListener('DOMContentLoaded', function() {
    // set min date on all date inputs to today
    var today = new Date().toISOString().split('T')[0];
    document.querySelectorAll('input[type="date"]').forEach(function(input) {
        input.setAttribute('min', today);
    });

    // scroll to guide booking when "Book a Guide" is clicked
    var hireBtn = document.getElementById('ne');
    if (hireBtn) {
        hireBtn.addEventListener('click', function() {
            var section = document.querySelector('.reservation');
            if (section) section.scrollIntoView({ behavior: 'smooth' });
        });
    }

    // tanguar haor houseboat booking
    var houseboatBtn = document.getElementById('seemanu');
    if (houseboatBtn) {
        houseboatBtn.addEventListener('click', function() {
            bookPlace('Tanguar Haor Houseboat Experience', 6000);
        });
    }

    // place booking form submission via AJAX
    var placeForm = document.getElementById('placeBookingForm');
    if (placeForm) {
        placeForm.addEventListener('submit', function(e) {
            e.preventDefault();

            var data = {
                name: document.getElementById('placeBookingName').value,
                phone: document.getElementById('placeBookingPhone').value,
                date: document.getElementById('placeBookingDate').value,
                persons: document.getElementById('placeBookingPersons').value,
                place_name: document.getElementById('bookPlaceName').textContent,
                price: parseInt(document.getElementById('bookPlacePrice').textContent) || 0
            };

            fetch('/book-place', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(function(res) { return res.json(); })
            .then(function(result) {
                if (result.success) {
                    alert(result.message);
                    closeModal('bookPlaceModal');
                    placeForm.reset();
                } else {
                    alert(result.error || 'Booking failed.');
                }
            })
            .catch(function() {
                alert('Something went wrong. Please try again.');
            });
        });
    }

    // star rating interaction
    document.querySelectorAll('#reviewForm .star').forEach(function(star) {
        star.addEventListener('click', function() {
            var val = parseInt(this.getAttribute('data-value'));
            document.getElementById('reviewRating').value = val;

            document.querySelectorAll('#reviewForm .star').forEach(function(s) {
                var sVal = parseInt(s.getAttribute('data-value'));
                if (sVal <= val) {
                    s.classList.add('active');
                } else {
                    s.classList.remove('active');
                }
            });
        });
    });

    // review form submission
    var reviewForm = document.getElementById('reviewForm');
    if (reviewForm) {
        reviewForm.addEventListener('submit', function(e) {
            e.preventDefault();

            var rating = document.getElementById('reviewRating').value;
            if (rating == 0) {
                alert('Please select a rating.');
                return;
            }

            var data = {
                destination_id: document.getElementById('reviewDestId').value,
                rating: parseInt(rating),
                comment: document.getElementById('reviewComment').value
            };

            fetch('/add-review', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            })
            .then(function(res) { return res.json(); })
            .then(function(result) {
                if (result.success) {
                    alert(result.message);
                    closeModal('reviewModal');
                } else {
                    alert(result.error || 'Failed to submit review.');
                }
            })
            .catch(function() {
                alert('Something went wrong.');
            });
        });
    }

    // initialize search
    setupSearch();

    // auto-dismiss flash messages after 5 seconds
    setTimeout(function() {
        document.querySelectorAll('.flash-message').forEach(function(msg) {
            msg.style.animation = 'slideIn 0.4s ease reverse';
            setTimeout(function() { msg.remove(); }, 400);
        });
    }, 5000);

    // newsletter subscription
    var newsletterForm = document.getElementById('newsletterForm');
    if (newsletterForm) {
        newsletterForm.addEventListener('submit', function(e) {
            e.preventDefault();
            var email = this.querySelector('input[type="email"]').value;
            alert('Thank you for subscribing! Check your email for exclusive offers.');
            this.reset();
        });
    }

    // destination page filters and sorting
    var priceFilter = document.getElementById('priceFilter');
    var sortBy = document.getElementById('sortBy');
    
    if (priceFilter || sortBy) {
        function applyFiltersAndSort() {
            var places = Array.from(document.querySelectorAll('.place-card'));
            var priceRange = priceFilter ? priceFilter.value : '';
            var sortType = sortBy ? sortBy.value : '';

            // filter by price
            if (priceRange) {
                places = places.filter(function(card) {
                    var priceText = card.querySelector('.place-price');
                    if (!priceText) return true;
                    var price = parseInt(priceText.textContent.match(/\d+/)[0]);
                    
                    if (priceRange === '0-500') return price < 500;
                    if (priceRange === '500-1000') return price >= 500 && price <= 1000;
                    if (priceRange === '1000+') return price > 1000;
                    return true;
                });
            }

            // sort
            if (sortType) {
                places.sort(function(a, b) {
                    if (sortType === 'name') {
                        var nameA = a.querySelector('.place-info h3').textContent;
                        var nameB = b.querySelector('.place-info h3').textContent;
                        return nameA.localeCompare(nameB);
                    } else if (sortType === 'price-low') {
                        var priceA = parseInt(a.querySelector('.place-price').textContent.match(/\d+/)[0]);
                        var priceB = parseInt(b.querySelector('.place-price').textContent.match(/\d+/)[0]);
                        return priceA - priceB;
                    } else if (sortType === 'price-high') {
                        var priceA = parseInt(a.querySelector('.place-price').textContent.match(/\d+/)[0]);
                        var priceB = parseInt(b.querySelector('.place-price').textContent.match(/\d+/)[0]);
                        return priceB - priceA;
                    }
                });
            }

            // show/hide cards
            document.querySelectorAll('.place-card').forEach(function(card) {
                card.style.display = places.includes(card) ? 'block' : 'none';
            });
        }

        if (priceFilter) priceFilter.addEventListener('change', applyFiltersAndSort);
        if (sortBy) sortBy.addEventListener('change', applyFiltersAndSort);
    }
});
