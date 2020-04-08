from flask import Blueprint, render_template, flash, redirect, request

api = Blueprint("api", __name__)

@api.route("/")
def about():
    return render_template("index.html")