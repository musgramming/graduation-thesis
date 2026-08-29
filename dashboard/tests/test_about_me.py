import requests

BASE_URL = r"http://127.0.0.1:8050/about_me"

response = requests.get(BASE_URL)

assert response.status_code == 200, f"Mong đợi status 200, nhận được {response.status_code}"
assert response.text is not None, f"Mong đợi có thông điệp"