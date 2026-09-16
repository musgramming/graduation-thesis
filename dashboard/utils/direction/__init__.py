import os
from dotenv import load_dotenv

from .engines.direction_plain import PageDirection as PageDirectionPlain
from .engines.direction_secure import PageDirection as PageDirectionSecure
from .exception import DashModeException

load_dotenv()



# Cho phép linh hoạt nhận diện biến môi trường, ưu tiên DASH_MODE hoặc MODE
mode = os.getenv("DASH_MODE") or os.getenv("MODE") or os.getenv("FLASK_ENV", "development")
mode = mode.lower().strip()



# Fail-fast: Báo lỗi ngay lập tức thay vì chạy ngầm với cấu hình sai lệch
if mode not in ("development", "production"):
    raise DashModeException(
        f"Lỗi cấu hình: Biến môi trường chế độ ('{mode}') không hợp lệ. "
        "Chỉ chấp nhận giá trị 'development' hoặc 'production'."
    )

# Chọn module tương ứng dựa trên mode đã được xác thực
PageDirection = PageDirectionSecure if mode == "production" else PageDirectionPlain

