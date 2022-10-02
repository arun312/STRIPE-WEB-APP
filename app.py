
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

import stripe
# This is your test secret API key.
stripe.api_key = 'sk_test_51LoYstSCQP9tLIEHALBPJAWNm4usoTNFQSAoujlYHyNQG4CnJ1RZsw8VLs0bhlShtaDn3ZSXzNzGULW255MUfLme00IVHSECqH'


app = Flask(__name__,
            static_url_path='', 
            static_folder='web/static')

app.config["upload_folder"] = 'web/static/images/'
app.config["upload_folder2"] = 'web/static/'

app.config['SECRET_KEY']='mysecret'
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


# This is your test secret API key.
# stripe.api_key = 'sk_test_51LoYstSCQP9tLIEHALBPJAWNm4usoTNFQSAoujlYHyNQG4CnJ1RZsw8VLs0bhlShtaDn3ZSXzNzGULW255MUfLme00IVHSECqH'

app = Flask(__name__,
            static_url_path='',
            static_folder='public')


@app.before_request 
def before_request():
    g.user= None
    if 'user' in session:
        g.user = session['user']

@app.route("/")
def index():
    return render_template('index.html')

@app.route("/user_home")
def user_home():
    if g.user:
        query="SELECT * FROM PLAN"
        detail=selection(query)
        item=[]
        if detail!=False:
            for d in detail:
                x={
                    'name':d[0],
                    'a':d[1],
                    'b':d[2],
                    'c':d[3],
                    'd':d[4],
                    'e':d[5],
                    'f':d[6],
                }
                item.append(x)
        return render_template('user_home.html',item=item)
    return redirect('/login')

@app.route("/login", methods=['GET','POST'])
def login():
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

@app.route("/sign_up", methods=['GET','POST'])                 
def signup():
    if request.method=='POST':
        query="SELECT Count(*) FROM 'USER' WHERE `user_email`='%s'"%(request.form['email'])
        detail=selection(query)
        if detail!=False:
            for d in detail:
                if d[0]>0:
                    return render_template('register.html',id='500')
                else:
                    query="INSERT INTO 'USER'(user_name,user_email,user_password) values('%s','%s','%s')"%(request.form['name'],request.form['email'],request.form['password'])
                    detail=inUP(query)
                    if detail!=False:
                        return render_template('register.html',id='200')
        return render_template('register.html',id='404')
                    
    return render_template('register.html')

@app.route("/logout",methods=['GET','POST'])                 #new
def admin_logout():
    session['user'] = None
    return redirect('/')  

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
