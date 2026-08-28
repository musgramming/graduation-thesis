import os
from dotenv import load_dotenv
from flask import Flask
from dash import Dash
from flask_cors import CORS

from main_layout import app_layout
from api.not_access import api_bp as not_access_bp


server = Flask(__name__)
server.register_blueprint(not_access_bp)
CORS(server, resources={r"/*": {"origins": "*"}})


app = Dash(
    name="My App",
    server=server,
    use_pages=True,
    external_stylesheets=["/assets/bootstrap/css/bootstrap.min.css"],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
        {"name": "description", "content": "Hệ thống phân tích và trực quan hóa phổ điểm thi tốt nghiệp THPT phục vụ đồ án tốt nghiệp."},
        {"property": "og:title", "content": "Hệ thống Phân tích Phổ điểm THPT"},
        {"property": "og:description", "content": "Khám phá phổ điểm thi tốt nghiệp THPT qua các góc nhìn phân tích dữ liệu trực quan."},
        {"property": "og:type", "content": "website"},
    ]
)

app.layout = app_layout


if __name__ == "__main__":
    load_dotenv()

    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", 8050))
    debug = None
    match os.getenv("MODE"):
        case "production":
            debug = False
        case "development":
            debug = True
        case _:
            debug = False

    app.run(
        host=host,
        port=port,
        debug=debug if debug is None else True,
    )