import pytest
import requests

BASE_URL = "http://127.0.0.1:8050"

def test_about_me_page():
    response = requests.get(f"{BASE_URL}/about-me")
    
    assert response.status_code == 200, (
        f"Endpoint /about-me: Mong đợi status 200, nhận được {response.status_code}"
    )
    assert response.text, (
        "Endpoint /about-me: Nội dung trả về bị trống!"
    )