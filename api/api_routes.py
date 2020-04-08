from flask import Blueprint, render_template, flash, redirect, request

api_routes = Blueprint("api_routes", __name__)

@api_routes.route("/about")
def about():
    return {"something": "value"}

@api_routes.route("")
def register():
    return {"something": "value"}