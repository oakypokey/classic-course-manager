from flask import Blueprint, render_template, flash, redirect, request

index_route = Blueprint("index", __name__)

@index_route.route("/")
def index():
    return index_route.send_static_file("index.html")