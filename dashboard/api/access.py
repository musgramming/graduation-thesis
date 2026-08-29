from flask import Blueprint, Response

about_me = open("about_me.txt", mode="r", encoding = "utf-8").read()

api_bp = Blueprint("not_accessing_api", __name__)



@api_bp.get("/about_me")
@api_bp.get("/api/about-me")
def show_about_me():
    return Response(about_me, 200, mimetype="text/plain")