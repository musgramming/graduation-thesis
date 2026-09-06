from pathlib import Path
from flask import Blueprint, Response

current_dir = Path(__file__).resolve().parent
robots_path = current_dir / "about_me.txt"

robots = robots_path.read_text(encoding="utf-8")

api_bp = Blueprint("not_accessing_api", __name__)


@api_bp.get("/api")
def access():
    return Response("Access denied", 403)



@api_bp.get("/robots.txt")
@api_bp.get("/api/robots.txt")
def access_robots():
    return Response(robots, 200, mimetype="text/plain")
