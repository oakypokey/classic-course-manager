import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

app = Flask(__name__, static_folder='../build', static_url_path='/')

@app.route('/')
def index():
    return "application.send_static_file('index.html')"

@app.route('/api/something')
def something():
    return {"foo": "bar"}