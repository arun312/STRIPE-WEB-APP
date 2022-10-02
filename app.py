
from traceback import print_tb
# from dateutil import parser
from flask import Flask, request, jsonify,render_template,redirect,url_for,send_file,session,g,Response
from flask import json
import datetime
import sqlite3
import os
import logging
import json
import urllib.request
from math import sin, cos, sqrt, atan2, radians


app = Flask(__name__,
            static_url_path='', 
            static_folder='web/static')

app.config["upload_folder"] = 'web/static/images/'
app.config["upload_folder2"] = 'web/static/'

app.config['SECRET_KEY']='mysecret'
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)

@app.route("/")
def index():
    return render_template('index.html')
