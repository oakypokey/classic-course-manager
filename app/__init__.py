import os
from dotenv import load_dotenv
from flask import Flask, request, jsonify, Response
import requests
import json
from datetime import date
from app.dataAPI.academic_cal import getAcademicCalendarInfo
from app.dataAPI.course_methods import getAllCourseInfo

load_dotenv()

app = Flask(__name__, static_folder='../build', static_url_path='/')

@app.route('/')
def index():
    return app.send_static_file('index.html')

@app.route('/api/something')
def something():
    return {"foo": "bar"}

@app.route('/api/getinfo')
def get_info():
    return Response(getAllCourseInfo(request.args.get('crn', type = str)), mimetype='application/json')

@app.route('/api/getacademiccalinfo')
def get_academic_cal_info():
    return Response(json.dumps(getAcademicCalendarInfo()), mimetype='application/json')
    

def create_app():
    return app