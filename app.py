
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

YOUR_DOMAIN = 'https://richpanel-flask-app.herokuapp.com/'
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
    return render_template('index.html')

@app.route("/user_home")
def user_home():
    if g.user:
        query="SELECT * FROM PLAN"
        detail=selection(query)
        item=[]
        count=0
        if detail!=False:
            for d in detail:
                lst=[x for x in d[0]]
                x={
                    'name':d[0],
                    'a':d[1],
                    'b':d[2],
                    'c':d[3],
                    'd':d[4],
                    'e':d[5],
                    'f':d[6],
                    'fl':lst[0]
                }
                item.append(x)
        query="SELECT COUNT(*) FROM PAYMENTS WHERE user_id='%s'"%(g.user[0])
        detail=selection(query)
        if detail!=False:
            for d in detail:
                count=d[0]
        return render_template('user_home.html',item=item,count=count)
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

@app.route("/logout",methods=['GET','POST'])                 
def admin_logout():
    session['user'] = None
    return redirect('/')  

@app.route("/user_manage",methods=['GET','POST'])                
def user_manage():
    if g.user:
        if request.method=='POST':
            query="DELETE FROM PAYMENTS WHERE payment_id='%s'"%(request.form['id'])
            detail=inUP(query)
            if detail!=False:
                return redirect('/user_manage?id=200')
        query="SELECT * FROM PAYMENTS WHERE user_id='%s'"%(g.user[0])
        detail=selection(query)
        item=[]
        if detail!=False:
            for d in detail:
                x={
                    'name':d[2],
                    'id':d[0]
                }
                item.append(x)
        return render_template('user_manage.html',item=item)

    return redirect('/login')
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

@app.route('/create-checkout-session', methods=['POST'])
def create_checkout_session():
    try:
        prices = stripe.Price.list(
            lookup_keys=[request.form['lookup_key']],
            expand=['data.product']
        )

        checkout_session = stripe.checkout.Session.create(
            line_items=[
                {
                    'price': prices.data[0].id,
                    'quantity': 1,
                },
            ],
            mode='subscription',
            success_url=YOUR_DOMAIN +
            '/success?session_id={CHECKOUT_SESSION_ID}&product='+request.form['lookup_key'],
            cancel_url=YOUR_DOMAIN + '/cancel',
        )
        return redirect(checkout_session.url, code=303)
    except Exception as e:
        print(e)
        return "Server error", 500

@app.route('/create-portal-session', methods=['POST'])
def customer_portal():
    # For demonstration purposes, we're using the Checkout session to retrieve the customer ID.
    # Typically this is stored alongside the authenticated user in your database.
    checkout_session_id = request.form.get('session_id')
    checkout_session = stripe.checkout.Session.retrieve(checkout_session_id)

    # This is the URL to which the customer will be redirected after they are
    # done managing their billing with the portal.
    return_url = YOUR_DOMAIN

    portalSession = stripe.billing_portal.Session.create(
        customer=checkout_session.customer,
        return_url=return_url,
    )
    return redirect(portalSession.url, code=303)

@app.route('/webhook', methods=['POST'])
def webhook_received():
    # Replace this endpoint secret with your endpoint's unique secret
    # If you are testing with the CLI, find the secret by running 'stripe listen'
    # If you are using an endpoint defined with the API or dashboard, look in your webhook settings
    # at https://dashboard.stripe.com/webhooks
    webhook_secret = 'whsec_12345'
    request_data = json.loads(request.data)

    if webhook_secret:
        # Retrieve the event by verifying the signature using the raw body and secret if webhook signing is configured.
        signature = request.headers.get('stripe-signature')
        try:
            event = stripe.Webhook.construct_event(
                payload=request.data, sig_header=signature, secret=webhook_secret)
            data = event['data']
        except Exception as e:
            return e
        # Get the type of webhook event sent - used to check the status of PaymentIntents.
        event_type = event['type']
    else:
        data = request_data['data']
        event_type = request_data['type']
    data_object = data['object']

    print('event ' + event_type)

    if event_type == 'checkout.session.completed':
        print('🔔 Payment succeeded!')
    elif event_type == 'customer.subscription.trial_will_end':
        print('Subscription trial will end')
    elif event_type == 'customer.subscription.created':
        print('Subscription created %s', event.id)
    elif event_type == 'customer.subscription.updated':
        print('Subscription created %s', event.id)
    elif event_type == 'customer.subscription.deleted':
        # handle subscription canceled automatically based
        # upon your subscription settings. Or if the user cancels it.
        print('Subscription canceled: %s', event.id)

    return jsonify({'status': 'success'})

##############
@app.route("/checkout")
def checkout():
    key=request.args.get('key')
    name=request.args.get('name')
    price=request.args.get('price')
    term=request.args.get('term')
    return render_template('checkout.html',key=key,name=name,price=price,term=term)

@app.route("/success")
def success():
    if g.user:
        product=str(request.args.get('product'))
        lst=[x for x in product]
        if lst[0]=='B':
            product='Basic'
        elif lst[0]=='S':
            product='Standard'
        elif lst[0]=='P':
            product='Premium'
        elif lst[0]=='R':
            product='Regular'
        if lst[1]=='Y':
            product=product+' Yearly'
        elif lst[1]=='M':
            product=product+' Monthly'
        query="INSERT INTO 'PAYMENTS'(user_id,user_plan) values('%s','%s')"%(g.user[0],product)
        detail=inUP(query)
        if detail!=False:
            return render_template('success.html')
    else:
        return redirect('/login')

@app.route("/cancel")
def cancel():
    return render_template('cancel.html')
