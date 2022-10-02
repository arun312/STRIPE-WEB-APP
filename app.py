
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


@app.before_request 
def before_request():
    g.user= None
    if 'user' in session:
        g.user = session['user']

@app.route("/")
def index():
    if g.user:
        return redirect('/user_home') 
    user=0
    if request.method == 'POST':
        email=request.form['email']
        password=request.form['password']
        query="SELECT user_id,user_name FROM USER WHERE user_email='%s' AND user_password='%s'"%(email,password)
        detail=selection(query)
        if detail!=False:
            for d in detail:
                session['user']=[d[0],d[1]]
                return redirect('/user_home')  
        return render_template('login.html',id='404',msg="INVALID CREDENTIALS")
    try:
        user=request.args.get('user')
    except Exception as e:
        print(e)
    return render_template('login.html',user=user)
###################### DATABASE ###################################

def inUP(query): #Insertion or Updation Queries
    try:
        connection = sqlite3.connect('database.db')       
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        connection.close()
        return True
    except Exception as e:
        print(e)
        return False

def selection(query):  #Selection Queries
    try:
        connection = sqlite3.connect('database.db')       # Connect to the database
        connection.row_factory = sqlite3.Row
        cursor =  connection.cursor()
        cursor.execute(query)
        connection.commit()
        rv = cursor.fetchall()
        connection.close()
        return rv
    except Exception as e:
        print(e)
        return False

####################### DATABASE END###################################
