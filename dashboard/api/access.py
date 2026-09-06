from pathlib import Path
from flask import Blueprint, Response

current_dir = Path(__file__).resolve().parent
about_me_path = current_dir / "about_me.txt"

about_me = about_me_path.read_text(encoding="utf-8")

api_bp = Blueprint("accessing_api", __name__)



@api_bp.get("/about-me")
@api_bp.get("/api/about-me")
def show_about_me():
    return Response(about_me, 200, mimetype="text/plain")