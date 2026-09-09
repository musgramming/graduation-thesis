import pytest
import requests

BASE_URL = "http://localhost:8050"

@pytest.mark.parametrize(
    "endpoint, expected_status, expected_content_type",
    [
        ("api", 403, None),
        ("robots.txt", 200, "text/plain"),
        ("api/robots.txt", 200, "text/plain"),
    ]
)
def test_dashboard_endpoints(endpoint, expected_status, expected_content_type):
    full_url = f"{BASE_URL}/{endpoint}"
    response = requests.get(full_url)
    
    assert response.status_code == expected_status, (
        f"Endpoint /{endpoint}: Mong đợi status {expected_status}, nhận được {response.status_code}"
    )
    
    if endpoint == "api":
        assert response.text == "Access denied", (
            f"Endpoint /api: Mong đợi nội dung 'Access denied', nhận được '{response.text}'"
        )
    
    if expected_content_type:
        content_type = response.headers.get("content-type", "")
        assert expected_content_type in content_type, (
            f"Endpoint /{endpoint}: MimeType '{content_type}' không chứa '{expected_content_type}'"
        )