
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


application = Flask(__name__,
            static_url_path='', 
            static_folder='web/static')

application.config["upload_folder"] = 'web/static/images/'
application.config["upload_folder2"] = 'web/static/'

application.config['SECRET_KEY']='mysecret'
log = logging.getLogger('werkzeug')
log.setLevel(logging.ERROR)


@application.before_request 
def before_request():
    g.user= None
    if 'user' in session:
        g.user = session['user']

@application.route("/", methods=['GET','POST'])                 
def index():
    return render_template('index.html')

@application.route("/login", methods=['GET','POST'])                 
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

@application.route("/sign_up", methods=['GET','POST'])                 
def signup():
    if request.method=='POST':
        user_type=request.form['UserType']
        mname=user_type.lower()+'_email'
        query="SELECT Count(*) FROM '%s' WHERE `%s`='%s'"%(user_type,mname,request.form['email'])
        detail=selection(query)
        if detail!=False:
            for d in detail:
                if d[0]>0:
                    return render_template('register.html',id='500')
                else:
                    uname=user_type+'_name'
                    upass=user_type+'_password'
                    uadd=user_type+'_address'
                    uphone=user_type+'_ph'
                    query="INSERT INTO '%s'(%s,%s,%s,%s,%s) values('%s','%s','%s','%s','%s')"%(user_type,uname,mname,upass,uadd,uphone,request.form['name'],request.form['email'],request.form['password'],request.form['address'],request.form['phone'])
                    detail=inUP(query)
                    if detail!=False:
                        return render_template('register.html',id='200')
        return render_template('register.html',id='404')
                    
    return render_template('register.html')

@application.route("/logout",methods=['GET','POST'])                 #new
def admin_logout():
    session['admin'] = None
    session['agent'] = None
    session['user'] = None

    return redirect('/')  

#################### Agent Start #################################
@application.route("/agent_index", methods=['GET','POST'])                 
def agent_index():
    if g.agent:
        item=[]
        query="SELECT acco_id,acco_name FROM ACCOMODATION WHERE acco_agentid='%s'"%(g.agent[0])
        detail=selection(query)
        if detail!=False:
            for d in detail:
                query="SELECT date,user_id,req_id FROM REQUESTS WHERE acco_id='%s' AND status=0"%(d[0])
                detail=selection(query)
                if detail!=False:
                    for e in detail:
                        query="SELECT user_name,user_address FROM USER WHERE user_id='%s'"%(e[1])
                        detail=selection(query)
                        if detail!=False:
                            for f in detail:     
                                x={
                                    'req_id':e[2],
                                    'user_name':f[0],
                                    'user_address':f[1][0:8]+"..",
                                    'date':e[0],
                                    'acco_name':d[1]
                                }
                                item.append(x)
        item2=[]
        query="SELECT acco_id,acco_name FROM ACCOMODATION WHERE acco_agentid='%s' AND acco_type IS NOT 'nhome'"%(g.agent[0])
        detail=selection(query)
        if detail!=False:
            for d in detail:
                query="SELECT date,user_id,req_id,payment FROM REQUESTS WHERE acco_id='%s' AND status=1"%(d[0])
                detail=selection(query)
                if detail!=False:
                    for e in detail:
                        query="SELECT user_name,user_address FROM USER WHERE user_id='%s'"%(e[1])
                        detail=selection(query)
                        if detail!=False:
                            for f in detail:     
                                x={
                                    'req_id':e[2],
                                    'user_name':f[0],
                                    'user_address':f[1][0:8]+"..",
                                    'date':e[0],
                                    'acco_name':d[1],
                                    'payment':e[3]
                                }
                                item2.append(x)
        return render_template('agent_index.html',name=g.agent[1],item=item,item2=item2)
    else:
        return redirect('/login?user=1')

@application.route("/agent_action", methods=['GET','POST'])                 
def agent_action():
    response={
        "status":404
    }
    if g.agent:
        data=json.loads(request.data)
        query="UPDATE REQUESTS set status='%s' WHERE req_id='%s'"%(data['action'],data['req_id'])
        detail=inUP(query)
        if detail!=False:
            response={
                "status":200
            }
    return response

@application.route("/agent_add", methods=['GET','POST'])                 
def agent_add():
    if g.agent:
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        if request.method=='POST':
            place=request.form['place']
            coordinates=getcoordinates(place)
            query="INSERT INTO ACCOMODATION (acco_agentid,acco_agentname,acco_name,acco_type,acco_description,acco_place,acco_coordinates,acco_date) values('%s','%s','%s','%s','%s','%s','%s','%s')"%(g.agent[0],g.agent[1],request.form['name'],request.form['type'],request.form['description'],request.form['place'],coordinates,dt_string)
            detail=inUP(query)
            if detail!=False:
                query="SELECT acco_id from ACCOMODATION ORDER BY acco_id DESC LIMIT 1"
                detail=selection(query)
                if detail!=False:
                    for d in detail:
                        id=d[0]
                    return render_template('agent_add2.html',type=request.form['type'],id=id)
            return render_template('agent_add.html',name=g.agent[1])
        return render_template('agent_add.html',name=g.agent[1])
    else:
        return redirect('/login')

@application.route("/agent_add2", methods=['GET','POST'])                 
def agent_add2():
    if request.method=='POST':
        data=request.form
        if data['type']=='hostel':
            query="UPDATE ACCOMODATION set acco_qty='%s' WHERE acco_id='%s'"%(data['acco_qty'],data['id'])
            try:
                inUP(query)
            except:
                print('Error')

        query="UPDATE ACCOMODATION set acco_price='%s',acco_landmark='%s',acco_size='%s',acco_gender='%s',acco_duration='%s',acco_qty='%s',acco_misc='%s' WHERE acco_id='%s'"%(data['price'],data['landmark'],data['size'],data['Gender'],data['duration'],data['acco_qty'],data['acco_misc'],data['id'])
        try:
            detail=inUP(query)
            if detail!=False:
                directory= str(data['id'])
                parent_dir = 'web/static/acco_images'
                path = os.path.join(parent_dir, directory)
                os.mkdir(path)
                files = request.files.getlist('img[]')
                # image = request.files["img"]
                n=.1
                for image in files:
                    x=float(data['id'])+n
                    image.save(os.path.join('web/static/acco_images',directory, str(x)+'.png'))
                    n=n+.1
                return render_template('agent_add2.html',sucess='1')
        except Exception as e:
            print(e)
            return render_template('agent_add2.html',sucess='0')

@application.route("/agent_viewacco", methods=['GET','POST'])                 
def agent_viewacco():
    if g.agent:
        item=[]
        query="SELECT acco_id,acco_name,acco_price,acco_date FROM ACCOMODATION WHERE acco_agentid='%s'"%(g.agent[0])
        detail=selection(query)
        if detail!=False:
            for d in detail:
                x={
                    'acco_id':d[0],
                    'acco_name':d[1],
                    'acco_price':d[2],
                    'acco_date':d[3]
                }
                item.append(x)
        return render_template('agent_view accomodations.html',item=item)

@application.route("/agent_delacco", methods=['GET','POST'])                 
def agent_delacco():
    if g.agent:
        data=json.loads(request.data)  
        query="DELETE FROM ACCOMODATION WHERE acco_id='%s'"%(data['id'])
        print(query)
        inUP(query)
        return render_template('agent_editacco.html',status='200')

@application.route("/agent_editacco", methods=['GET','POST'])                 
def agent_editacco():
    if g.agent:
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        if request.method=='POST':
            data=request.form
            query="UPDATE ACCOMODATION set acco_name='%s',acco_price='%s',acco_description='%s',acco_date='%s' WHERE acco_id='%s'"%(data['name'],data['price'],data['description'],dt_string,data['id'])
            inUP(query)
            return render_template('agent_editacco.html',status='200')
            
        item=[]
        query="SELECT acco_id,acco_name,acco_price,acco_description FROM ACCOMODATION WHERE acco_id='%s'"%(request.args.get('id'))
        detail=selection(query)
        if detail!=False:
            for d in detail:
                x={
                    'acco_id':d[0],
                    'acco_name':d[1],
                    'acco_price':d[2],
                    'acco_description':d[3]
                }
                item.append(x)
        return render_template('agent_editacco.html',item=item)

##################### Agent End ##################################
#################### User Start ##################################

@application.route("/search_hostels", methods=['GET','POST'])                 
def search_hostels():
    if request.method =='POST':
        data=json.loads(request.data)
        qA=""
        qB=""
        qC=""
        search_text=data['search_text']
        price=data['price']
        gender=data['gender']
        roomtype=data['roomtype']

        if str(price)!='0':
            qA=" AND acco_price < '%s'"%(price)
        
        if str(gender)!='0':
            qB=" AND acco_gender = '%s'"%(gender)

        if str(roomtype)!='0':
            qC=" AND acco_misc = '%s'"%(roomtype)

        location_y=getcoordinates(search_text)

        if search_text=='None':
            response={
                'status':500
            }
            return response
        else:
            query="SELECT acco_id,acco_name,acco_agentname,acco_date,acco_price,acco_coordinates,acco_gender FROM ACCOMODATION WHERE acco_type='hostel'"+qA+qB+qC
            detail=selection(query)
            item=[]
            if detail!=False:
                for d in detail:
                    location_x=d[5]
                    location_x=location_x.replace('[', '')
                    location_x=location_x.replace(']', '')
                    location_x=location_x.split(', ')
                    distance=distancecalculator(location_x,location_y)
                    if distance<2.5:
                        x={
                            'acco_id':d[0],
                            'acco_name':d[1],
                            'acco_agent':d[2],
                            'acco_time':d[3],
                            'acco_price':d[4],
                            'acco_gender':d[6]
                        }
                        item.append(x)
                response={
                    'status':200,
                    'item':item
                }
                return response
    return render_template('search_hostels.html')

@application.route("/search_pg", methods=['GET','POST'])                 
def search_pg():
    if request.method =='POST':
        data=json.loads(request.data)
        qA=""
        qB=""
        qC=""
        search_text=data['search_text']
        price=data['price']
        gender=data['gender']
        roomtype=data['roomtype']

        if str(price)!='0':
            qA=" AND acco_price < '%s'"%(price)
        
        if str(gender)!='0':
            qB=" AND acco_gender = '%s'"%(gender)

        if str(roomtype)!='0':
            qC=" AND acco_misc = '%s'"%(roomtype)

        location_y=getcoordinates(search_text)

        if search_text=='None':
            response={
                'status':500
            }
            return response
        else:
            query="SELECT acco_id,acco_name,acco_agentname,acco_date,acco_price,acco_coordinates,acco_gender FROM ACCOMODATION WHERE acco_type='pg'"+qA+qB+qC
            detail=selection(query)
            item=[]
            if detail!=False:
                for d in detail:
                    location_x=d[5]
                    location_x=location_x.replace('[', '')
                    location_x=location_x.replace(']', '')
                    location_x=location_x.split(', ')
                    distance=distancecalculator(location_x,location_y)
                    if distance<2.5:
                        x={
                            'acco_id':d[0],
                            'acco_name':d[1],
                            'acco_agent':d[2],
                            'acco_time':d[3],
                            'acco_price':d[4],
                            'acco_gender':d[6]
                        }
                        item.append(x)
                response={
                    'status':200,
                    'item':item
                }
                return response
    return render_template('search_pg.html')

@application.route("/search_homerent", methods=['GET','POST'])                 
def search_homerent():
    if request.method =='POST':
        data=json.loads(request.data)
        qA=""
        qB=""
        qC=""
        search_text=data['search_text']
        price=data['price']
        gender=data['gender']
        roomtype=data['roomtype']

        if str(price)!='0':
            qA=" AND acco_price < '%s'"%(price)
        
        if str(gender)!='0':
            qB=" AND acco_gender = '%s'"%(gender)

        if str(roomtype)!='0':
            qC=" AND acco_misc = '%s'"%(roomtype)

        location_y=getcoordinates(search_text)

        if search_text=='None':
            response={
                'status':500
            }
            return response
        else:
            query="SELECT acco_id,acco_name,acco_agentname,acco_date,acco_price,acco_coordinates,acco_gender FROM ACCOMODATION WHERE acco_type='homerent'"+qA+qB+qC
            detail=selection(query)
            item=[]
            if detail!=False:
                for d in detail:
                    location_x=d[5]
                    location_x=location_x.replace('[', '')
                    location_x=location_x.replace(']', '')
                    location_x=location_x.split(', ')
                    distance=distancecalculator(location_x,location_y)
                    if distance<2.5:
                        x={
                            'acco_id':d[0],
                            'acco_name':d[1],
                            'acco_agent':d[2],
                            'acco_time':d[3],
                            'acco_price':d[4],
                            'acco_gender':d[6]
                        }
                        item.append(x)
                response={
                    'status':200,
                    'item':item
                }
                return response
    return render_template('search_homerent.html')

@application.route("/search_nhome", methods=['GET','POST'])                 
def search_nhome():
    if request.method =='POST':
        data=json.loads(request.data)
        qA=""
        qB=""
        qC=""
        search_text=data['search_text']
        price=data['price']
        gender=data['gender']
        roomtype=data['roomtype']

        if str(price)!='0':
            qA=" AND acco_price < '%s'"%(price)
        
        if str(gender)!='0':
            qB=" AND acco_gender = '%s'"%(gender)

        if str(roomtype)!='0':
            qC=" AND acco_misc = '%s'"%(roomtype)

        location_y=getcoordinates(search_text)

        if search_text=='None':
            response={
                'status':500
            }
            return response
        else:
            query="SELECT acco_id,acco_name,acco_agentname,acco_date,acco_price,acco_coordinates,acco_gender FROM ACCOMODATION WHERE acco_type='nhome'"+qA+qB+qC
            detail=selection(query)
            item=[]
            if detail!=False:
                for d in detail:
                    location_x=d[5]
                    location_x=location_x.replace('[', '')
                    location_x=location_x.replace(']', '')
                    location_x=location_x.split(', ')
                    distance=distancecalculator(location_x,location_y)
                    if distance<2.5:
                        x={
                            'acco_id':d[0],
                            'acco_name':d[1],
                            'acco_agent':d[2],
                            'acco_time':d[3],
                            'acco_price':d[4],
                            'acco_gender':d[6]
                        }
                        item.append(x)
                response={
                    'status':200,
                    'item':item
                }
                return response
    return render_template('search_nhome.html')

@application.route("/user_accodetails", methods=['GET','POST'])                 
def user_accodetails():
    if g.user:
        query="SELECT acco_id,acco_name,acco_price,acco_duration,acco_description,acco_qty,acco_type FROM ACCOMODATION WHERE acco_id='%s'"%(request.args.get('id'))
        detail=selection(query)
        item=[]
        if detail!=False:
            for d in detail:
                    query="SELECT COUNT(*) FROM REQUESTS WHERE acco_id='%s' AND status='1'"%(request.args.get('id'))
                    detail=selection(query)
                    if detail!=False:
                        for e in detail:
                            n=int(d[5])-int(e[0]) 
                    try:
                        dir='web/static/acco_images/'+str(d[0])
                        list = os.listdir(dir) # dir is your directory path
                        number_files = len(list)
                    except Exception as e:
                        print(e)
                        number_files=0
                    response= {
                        "status":200,
                        "acco_id":d[0],
                        "acco_name":d[1],
                        "acco_price":d[2],
                        "acco_duration":d[3],
                        "acco_description":d[4],
                        "acco_qty":d[5],
                        "acco_type":d[6],
                        "r":n,
                        "pic_count":number_files
                    }
                    item.append(response)
        return render_template('user_accodetails.html',item=item)
    else:
        return redirect('/login')
 
@application.route("/user_requestacco", methods=['GET','POST'])                 
def user_requestacco():
    response={
        'status':404
    }
    if g.user:
        data=json.loads(request.data)
        query="SELECT COUNT(*) FROM REQUESTS WHERE acco_id='%s' AND status=1"%(data['id'])
        print(query)
        detail=selection(query)
        if detail!=False:
            for d in detail:     
                x=float(data['acco_qty'])
                t=d[0]
                if (t<=x):
                    now = datetime.datetime.now()
                    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
                    query="INSERT INTO REQUESTS(user_id,acco_id,status,date) values('%s','%s','%s','%s')"%(g.user[0],data['id'],0,dt_string)
                    detail=inUP(query)
                    if detail!=False:
                        response={
                            'status':200
                        }
    return response

@application.route("/user_profile", methods=['GET','POST'])                 
def user_profile():
    if g.user:
        query="SELECT user_name,user_email,user_address,user_ph FROM USER WHERE user_id='%s'"%(g.user[0])
        detail=selection(query)
        item=[]
        if detail!=False:
            for d in detail:
                response={
                    "status":200,
                    "user_name":d[0],
                    "user_email":d[1],
                    "user_phone":d[3],
                    "user_address":d[2]
                }
                item.append(response)
                return render_template('user_profile.html',item=item)
    else:
        return redirect('/login')     

@application.route("/user_notifications", methods=['GET','POST'])                 
def user_notifications():
    if g.user:
        query="SELECT req_id,acco_id,status,payment FROM REQUESTS WHERE user_id='%s' AND status IS NOT 3 ORDER BY req_id DESC"%(g.user[0])
        detail=selection(query)
        item=[]
        if detail!=False:
            for d in detail:
                query="SELECT acco_name,acco_price,acco_agentid FROM ACCOMODATION WHERE acco_id='%s'"%(d[1])
                detail=selection(query)
                if detail!=False:
                    for e in detail:
                        query="SELECT agent_name,agent_email,agent_ph FROM AGENT WHERE agent_id='%s'"%(e[2])
                        detail=selection(query)
                        if detail!=False:
                            for f in detail:
                                agent_name=f[0]
                                agent_email=f[1]
                                agent_ph=f[2]

                        if d[2]=='0':
                            status='pending'
                        elif d[2]=='1':
                            status='Accepted'
                        else:
                            status='Declined'
                        x={
                            'req_id':d[0],
                            'acco_name':e[0],
                            'acco_price':e[1],
                            'status':status,
                            'payment':d[3],
                            'agent_name':agent_name,
                            'agent_email':agent_email,
                            'agent_ph':agent_ph
                        }
                        item.append(x)
        return render_template('user_notifications.html',item=item)
    else:
        return redirect('/login')

@application.route("/payment", methods=['GET','POST'])                 
def payment():
    if g.user:
        if request.method=="POST":
            response={
                'status':404
            }
            req_id=request.args.get('req_id')
            query="UPDATE REQUESTS set payment='1' WHERE req_id='%s'"%(req_id)
            detail=inUP(query)
            if detail!=False:
                return render_template('payment.html',sucess="1")
            return render_template('payment.html',sucess="1")

        return render_template('payment.html')

#################### User End ###################################
###################### ADMIN ###################################
@application.route("/admin_home", methods=['GET','POST'])                 
def admin_home():
    if g.admin:
        now = datetime.datetime.now()
        dt_string = now.strftime("%d/%m/%Y")
        query="SELECT COUNT(*) FROM REQUESTS WHERE date LIKE '%s'"%(dt_string+'%')
        detail=selection(query)
        if detail!=False:
            for d in detail:
                a=d[0]
        query="SELECT COUNT(*) FROM REQUESTS"
        detail=selection(query)
        if detail!=False:
            for d in detail:
                b=d[0]
        query="SELECT COUNT(*) FROM USER"
        detail=selection(query)
        if detail!=False:
            for d in detail:
                c=d[0]
        query="SELECT COUNT(*) FROM AGENT"
        detail=selection(query)
        if detail!=False:
            for d in detail:
                d=d[0]
                

        return render_template('admin_index.html',a=a,b=b,c=c,d=d)
    else:
        return redirect('/login?user=2')

@application.route("/admin_viewusers", methods=['GET','POST'])                 
def admin_viewusers():
    if g.admin:
        item=[]
        query="SELECT * FROM USER"
        detail=selection(query)
        if detail!=False:
            for d in detail:
                x={
                    'name':d[1],
                    'email':d[2],
                    'address':d[4][0:10]+"..."
                } 
                item.append(x)
        return render_template('admin_viewusers.html',item=item)
    else:
        return redirect('/login')

@application.route("/admin_viewagents", methods=['GET','POST'])                 
def admin_viewagents():
    if g.admin:
        item=[]
        query="SELECT * FROM AGENT WHERE verification='1'"
        detail=selection(query)
        if detail!=False:
            for d in detail:
                x={
                    'name':d[1],
                    'email':d[2],
                    'address':d[4][0:10]+"..."
                } 
                item.append(x)
        return render_template('admin_viewagents.html',item=item)
    else:
        return redirect('/login')

@application.route("/admin_viewbookings", methods=['GET','POST'])                 
def admin_viewbookings():
    if g.admin:
        item=[]
        query="SELECT acco_id,user_id,date,status FROM REQUESTS WHERE status IS NOT 3"
        detail=selection(query)
        if detail!=False:
            for d in detail:
                query="SELECT acco_name FROM ACCOMODATION WHERE acco_id='%s'"%(d[0])
                detail=selection(query)
                if detail!=False:
                    for e in detail:
                        acco_name=e[0]
                query="SELECT user_name FROM USER WHERE user_id='%s'"%(d[1])
                detail=selection(query)
                if detail!=False:
                    for e in detail:
                        user_name=e[0]
                if d[3]=='0':
                    status='pending'
                elif d[3]=='1':
                    status='Accepted'
                else:
                    status='Declined'
                x={
                    'acco_name':acco_name,
                    'user_name':user_name,
                    'date':d[2],
                    'status':status
                }
                item.append(x)
        return render_template('admin_viewbookings.html',item=item)
    else:
        return redirect('/login')

@application.route("/admin_manageagents", methods=['GET','POST'])                 
def admin_manageagents():
    if g.admin:
        if request.method=='POST':
            response={
                'status':404
            }
            data=json.loads(request.data)
            id=data['agent_id']
            query="UPDATE AGENT set verification='%s' WHERE agent_id='%s'"%(data['action'],id)
            detail=inUP(query)
            if detail!=False:
                response={
                    'status':200
                }
            return response
        item=[]
        query="SELECT * FROM AGENT WHERE verification='0'"
        detail=selection(query)
        if detail!=False:
            for d in detail:
                x={ 
                    'agent_id':d[0],
                    'agent_name':d[1],
                    'agent_email':d[2],
                    'agent_address':d[4][0:10]+"..."
                } 
                item.append(x)
        return render_template('admin_manageagents.html',item=item)
    else:
        return redirect('/login')

#################### ADMIN END ###################################

@application.route('/send_ima')
def download_qn ():
    path = os.path.join('web/static/qn_pdf/', str(request.args.get('ex_id'))+'.pdf')
    return send_file(path, as_attachment=True)

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

if __name__ == "__main__":
    application.debug = True
    application.run(host='127.0.0.1')


