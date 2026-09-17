import os
from dotenv import load_dotenv

load_dotenv(override=True)

def get_standardized_mode() -> str:
    """
    Quét tất cả các biến môi trường có thể có của Dash/Flask,
    chuẩn hóa về một định dạng duy nhất.
    """
    # Thứ tự ưu tiên: DASH_MODE -> MODE -> FLASK_ENV -> mặc định "development"
    raw_mode = (
        os.getenv("DASH_MODE") 
        or os.getenv("MODE") 
        or os.getenv("mode")
        or os.getenv("FLASK_ENV") 
        or "development"
    )
    
    # Chuẩn hóa chuỗi (loại bỏ khoảng trắng, viết thường)
    normalized = raw_mode.strip().lower()
    
    # Bản đồ quy đổi các tên gọi tương đương của bên thứ 3 (Flask/Dash cũ)
    # Ví dụ: flask dùng 'prod' hay 'development', ta quy về chuẩn chung của mình
    mapping = {
        "prod": "production",
        "production": "production",
        "dev": "development",
        "development": "development",
        "local": "development"
    }
    
    return mapping.get(normalized, normalized)