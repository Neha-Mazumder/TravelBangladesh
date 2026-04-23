import requests
import sqlite3

BASE_URL = 'http://127.0.0.1:5000'
DB_PATH = 'travelbd.db'

def check_contacts():
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, message FROM contacts ORDER BY id DESC LIMIT 1")
        row = cursor.fetchone()
        if not row:
            print("No contacts found in database.")
            return None, None
        return row[0], row[1]

def run_test():
    session = requests.Session()
    
    # 1. Login
    login_url = f'{BASE_URL}/login'
    login_data = {'email': 'admin@travelbd.com', 'password': 'admin123'}
    print(f"Attempting login to {login_url}...")
    try:
        r_login = session.post(login_url, data=login_data, allow_redirects=True)
        print(f"Login status code: {r_login.status_code}")
        if 'Logout' not in r_login.text and '/logout' not in r_login.text:
            print("Login might have failed (couldn't find Logout link).")
    except Exception as e:
        print(f"Login failed: {e}")
        return

    # 2. Admin Dashboard
    dash_url = f'{BASE_URL}/admin/dashboard'
    r_dash = session.get(dash_url)
    print(f"Admin dashboard status: {r_dash.status_code}")
    
    # 3 & 4. Latest Contact Detail
    contact_id, full_message = check_contacts()
    if contact_id:
        contact_url = f'{BASE_URL}/admin/contact/{contact_id}'
        r_contact = session.get(contact_url)
        print(f"Contact detail page status: {r_contact.status_code}")
        
        if full_message in r_contact.text:
            print(f"SUCCESS: Full message found on page.")
        else:
            print(f"FAILURE: Full message NOT found on page.")
            # Print a snippet of the page to see what's there
            print("Page snippet:")
            print(r_contact.text[:500])
    else:
        print("Skipping contact check as no contacts exist.")

if __name__ == '__main__':
    run_test()
