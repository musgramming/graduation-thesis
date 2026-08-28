import requests

# Thay đổi base URL nếu app Flask của bạn chạy port khác
BASE_URL = "http://localhost:8050"
ENDPOINTS = [
    "api", 
    "robots.txt", 
    "api/robots.txt"
]

def test_endpoints(base_url: str, endpoint: str):
    full_url = f"{base_url}/{endpoint}"
    print(f"Đang kiểm tra: GET /{endpoint}")
    
    try:
        response = requests.get(full_url)
        print(f"-> Status: {response.status_code} | Content-Type: {response.headers.get('content-type')}")
        
        # Kiểm tra điều kiện dựa trên từng loại endpoint
        if endpoint == "api":
            assert response.status_code == 403, f"Mong đợi status 403, nhận được {response.status_code}"
            assert response.text == "Access denied", f"Mong đợi nội dung 'Access denied', nhận được '{response.text}'"
            print("-> [PASS] Route /api chặn thành công!")
        
        elif "robots.txt" in endpoint:
            assert response.status_code == 200, f"Mong đợi status 200, nhận được {response.status_code}"
            assert "text/plain" in response.headers.get("content-type", ""), "MimeType không phải text/plain"
            print(f"-> [PASS] Route /{endpoint} trả về nội dung robots.txt thành công!")
            print(f"-> Nội dung xem trước: {response.text.strip()[:50]}...")
            
    except Exception as e:
        print(f"-> [FAIL] Endpoint /{endpoint} gặp lỗi: {e}")

    print("-" * 40)

if __name__ == "__main__":
    for endpoint in ENDPOINTS:
        test_endpoints(BASE_URL, endpoint)