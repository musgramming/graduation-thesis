from flask import Blueprint, Response

robots = open("robots.txt", mode="r", encoding = "utf-8").read()

api_bp = Blueprint("api", __name__)


@api_bp.get("/api")
def access():
    return Response("Access denied", 403)



@api_bp.get("/robots.txt")
@api_bp.get("/api/robots.txt")
def access_robots():
    return Response(robots, 200, mimetype="text/plain")
