import os
import logging
from dotenv import load_dotenv
from flask import Flask
from dash import Dash
from flask_cors import CORS
from waitress import serve

from template_layout.main_layout import app_layout
from template_layout.callback import *
from api.access import api_bp as access_bp
from api.not_access import api_bp as not_access_bp
from utils.exception import unreachable
from utils.read_mode import get_standardized_mode
from utils.direction.exception import DashModeException


logging.getLogger('waitress.queue').setLevel(logging.ERROR)






# =============================================================================
# Ứng dụng Server Flask
# =============================================================================

server = Flask(__name__)

server.register_blueprint(access_bp)
server.register_blueprint(not_access_bp)


CORS(
    server, 
    resources={
        r"/*": {
            "origins": "*"
        }
    }
)






# =============================================================================
# Ứng dụng DASH
# =============================================================================


app = Dash(
    name="My App",
    title="Hệ thống Phân tích Phổ điểm THPT",
    server=server,
    use_pages=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "Hệ thống phân tích và trực quan hóa phổ điểm thi tốt nghiệp THPT phục vụ đồ án tốt nghiệp."},
        {"property": "og:title", "content": "Hệ thống Phân tích Phổ điểm THPT"},
        {"property": "og:description", "content": "Khám phá phổ điểm thi tốt nghiệp THPT qua các góc nhìn phân tích dữ liệu trực quan."},
        {"property": "og:type", "content": "website"},
    ]
)


mode = get_standardized_mode()


app.index_string = f"""
<!DOCTYPE html>
<html>
    <head>
        {{%metas%}}
        <title>{{%title%}}</title>
        {{%favicon%}}
        {{%css%}}
        <script>
            window.APP_ENV = "{mode}";
        </script>
    </head>
    <body>
        <!-- BẪY NOSCRIPT: Hiển thị cảnh báo nếu user tắt JavaScript -->
        <noscript>
            <div style="
                position: fixed; 
                top: 0; left: 0; 
                width: 100%; height: 100%; 
                background-color: #0f172a; 
                color: #f8fafc; 
                display: flex; 
                flex-direction: column; 
                justify-content: center; 
                align-items: center; 
                z-index: 999999; 
                font-family: system-ui, -apple-system, sans-serif; 
                text-align: center; 
                padding: 20px;
            ">
                <div style="max-width: 500px; padding: 30px; background: #1e293b; border-radius: 12px; border: 1px solid #334155; box-shadow: 0 10px 25px rgba(0,0,0,0.5);">
                    <h2 style="color: #ef4444; margin-top: 0; margin-bottom: 15px; font-size: 24px;">⚠️ Yêu cầu JavaScript</h2>
                    <p style="font-size: 15px; line-height: 1.6; color: #cbd5e1; margin-bottom: 20px;">
                        Ứng dụng này yêu cầu trình duyệt phải kích hoạt <b>JavaScript</b> để vận hành không gian giao diện và hệ thống điều hướng.
                    </p>
                    <p style="font-size: 13px; color: #94a3b8; margin: 0;">
                        Vui lòng bật lại JavaScript trên trình duyệt của bạn và tải lại trang (F5) để tiếp tục sử dụng.
                    </p>
                </div>
            </div>
        </noscript>

        {{%app_entry%}}
        <footer>
            {{%config%}}
            {{%scripts%}}
            {{%renderer%}}
        </footer>
    </body>
</html>
"""
app.layout = app_layout











if __name__ == "__main__":
    load_dotenv()

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8050))

    # Kiểm tra Fail-fast ngay lập tức
    if mode not in ("development", "production"):
        raise DashModeException(
            f"Lỗi cấu hình: Phát hiện biến môi trường không hợp lệ ('{mode}'). "
            "Hệ thống chỉ chấp nhận 'development' hoặc 'production'."
        )

    if (mode == "development"): 
        print(f"-> Đang khởi động Dash server tại http://{host}:{port} ...")
        app.run(
            host = host, 
            port = port, 
            debug = True
        )
        print("Đã tắt Dash server!")

    elif (mode == "production"):
        try: 
            print(f"-> Đang khởi động Waitress server tại http://{host}:{port} ...")
            serve(
                app.server, 
                host = host, 
                port = port, 
                threads = 8
            )
        except KeyboardInterrupt:
            print("Đã tắt Waitress server!")

    else:
        unreachable("Debug là None rồi!")