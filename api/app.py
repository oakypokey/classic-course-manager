import os
from dotenv import load_dotenv
from flask import Flask

load_dotenv()

application = Flask(__name__, static_folder='../build', static_url_path='/')

@application.route('/')
def index():
    return application.send_static_file('index.html')

@application.route('/api/something')
def something():
    return {"foo": "bar"}