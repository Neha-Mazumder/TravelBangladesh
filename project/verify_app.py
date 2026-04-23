import requests

url = "http://127.0.0.1:5000"
login_url = f"{url}/login"
email = "admin@travelbd.com"
password = "admin123"

session = requests.Session()

# 1. Log in
print(f"Attempting login as {email}...")
login_data = {"email": email, "password": password}
response = session.post(login_url, data=login_data)
print(f"Login Status Code: {response.status_code}")

# 2. Fetch Home Page
print("Fetching home page...")
home_response = session.get(url)
print(f"Home Page Status Code: {home_response.status_code}")

# 3. Confirm Content
html = home_response.text
has_admin = "Admin" in html
has_dashboard = "/admin/dashboard" in html

print(f"Contains 'Admin': {has_admin}")
print(f"Contains '/admin/dashboard': {has_dashboard}")

# 4. Check Login Page Load
login_page_response = requests.get(login_url)
print(f"Login Page Load Status Code: {login_page_response.status_code}")

if has_admin and has_dashboard:
    print("Verification Successful: Admin items found in navbar.")
else:
    print("Verification Failed: Admin items MISSING from navbar.")
