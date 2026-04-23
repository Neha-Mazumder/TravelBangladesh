import requests

session = requests.Session()
login_url = 'http://127.0.0.1:5000/login'
admin_dashboard_url = 'http://127.0.0.1:5000/admin/dashboard'

login_data = {'email': 'admin@travelbd.com', 'password': 'admin123'}
response = session.post(login_url, data=login_data)

dashboard_response = session.get(admin_dashboard_url)
html_content = dashboard_response.text

target_user_email = 'demo@gmail.com'
target_user_name = 'ss'

contains_registered_users = 'Registered Users' in html_content
contains_user_email = target_user_email in html_content
contains_user_name = target_user_name in html_content

print(f'Dashboard fetched: {dashboard_response.status_code == 200}')
print(f'Contains \"Registered Users\": {contains_registered_users}')
print(f'Contains user email: {contains_user_email}')
print(f'Contains user name: {contains_user_name}')
