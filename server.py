from flask import Flask
from dash import Dash 
import redis
import dash_bootstrap_components as dbc
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache

from main_layout import app_layout

server = Flask(__name__)



# # Thử kết nối tới Redis
# try:
#     # Bắt cả lỗi kết nối và lỗi quá thời hạn (Timeout)
#     r = redis.Redis(host='127.0.0.1', port=6379, socket_connect_timeout=1)
#     r.ping()
#     USE_REDIS = True
# except (redis.ConnectionError, redis.TimeoutError, TimeoutError, ConnectionError):
#     USE_REDIS = False

# # Cấu hình Cache dựa trên kết quả kiểm tra
# if USE_REDIS:
#     cache_config = {
#         'CACHE_TYPE': 'RedisCache',
#         'CACHE_REDIS_URL': 'redis://127.0.0.1:6379/0',
#         'CACHE_DEFAULT_TIMEOUT': 300
#     }
#     storage_uri = "redis://127.0.0.1:6379/1"
#     print("🚀 Redis detected! Caching & Limiting via Redis.")
# else:
#     cache_config = {
#         'CACHE_TYPE': 'SimpleCache', # Chạy tạm trên RAM của Flask
#         'CACHE_DEFAULT_TIMEOUT': 300
#     }
#     storage_uri = "memory://" # Lưu limiter tạm trong bộ nhớ máy
#     print("⚠️ Redis not found! Falling back to Simple Memory Cache.")

# cache = Cache(server, config=cache_config)

# limiter = Limiter(
#     get_remote_address,
#     app=server,
#     default_limits=["50 per minute", "10000 per day"],
#     storage_uri=storage_uri,
# )

# @server.errorhandler(429)
# def ratelimit_handler(e):
#     return "Hệ thống đang bận. Vui lòng đợi vài giây rồi thử lại!", 429


app = Dash(
    name = "My App",
    server=server,
    use_pages = True, 
    external_stylesheets = [
        # dbc.themes.BOOTSTRAP,
        "/assets/bootstrap/css/bootstrap.min.css"
    ], 
    external_scripts=[
        "/assets/bootstrap/js/bootstrap.bundle.min.js"
    ],
    prevent_initial_callbacks = True
    
)
app.layout = app_layout

if __name__ == "__main__":
    app.run(debug=True) 
