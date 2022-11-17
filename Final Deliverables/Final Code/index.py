from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re, random, smtplib, os, time, datetime
from flask_mail import Mail, Message


app = Flask(__name__)

app.secret_key = '12345'

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'care2'

mysql = MySQL(app)

mail= Mail(app)

app.config['MAIL_SERVER']='smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = 'customercareregistry22@gmail.com'
app.config['MAIL_PASSWORD'] = 'vxzttcjvdvrqeeve'
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)



@app.route('/', methods =['GET', 'POST'])
def index():
   if request.method == 'POST' and 'email' in request.form:
      email = request.form['email']
      cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      cursor.execute('SELECT * FROM subscriptions WHERE email = % s', (email, ))
      subscriptions = cursor.fetchone()
      if subscriptions:
         flash('This Email Is Already Subscribed')
      else:
         ts = time.time()
         timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('INSERT INTO subscriptions VALUES (%s, % s, % s)', (None, email, timestamp, ))
         mysql.connection.commit()
         flash('You have successfully Subscribed')
   return render_template('index.html')



@app.route('/customerlogin', methods =['GET', 'POST'])
def customerlogin():
   msgdecline = ''
   if request.method == 'POST' and 'cemail' in request.form and 'cpassword' in request.form:
      cemail = request.form['cemail']
      cpassword = request.form['cpassword']
      cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      cursor.execute('SELECT * FROM customers_details WHERE customer_email = % s AND customer_password = % s', (cemail, cpassword, ))
      customers_details = cursor.fetchone()
      if customers_details:
         session['loggedin'] = True
         session['cemail'] = customers_details['customer_email']
         msgsuccess = 'Logged in successfully !'
         return redirect(url_for('welcome'))
      else:
         msgdecline = 'Incorrect Email / Password !'
   return render_template('customerlogin.html', msgdecline = msgdecline)



@app.route('/agentlogin', methods =['GET', 'POST'])
def agentlogin():
   msgdecline = ''
   if request.method == 'POST' and 'aemail' in request.form and 'apassword' in request.form:
      aemail = request.form['aemail']
      apassword = request.form['apassword']
      cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      cursor.execute('SELECT * FROM agent_information WHERE agent_email = % s AND agent_password = %s', (aemail, apassword,))
      agent_information = cursor.fetchone()
      if agent_information:
         session['loggedin'] = True
         session['aemail'] = agent_information['agent_email']
         msgsuccess = 'Logged in successfully !'
         return redirect(url_for('agentdashboard'))
      else:
         msgdecline = 'Incorrect Email / Password !'
   return render_template('agentlogin.html', msgdecline = msgdecline)



@app.route('/adminlogin', methods =['GET', 'POST'])
def adminlogin():
   msgdecline = ''
   if request.method == 'POST' and 'adminusername' in request.form and 'adminpassword' in request.form:
      adminusername = request.form['adminusername']
      adminpassword = request.form['adminpassword']
      cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      cursor.execute('SELECT * FROM admin_details WHERE admin_username = % s AND admin_password = % s', (adminusername, adminpassword, ))
      admin = cursor.fetchone()
      if admin:
         session['loggedin'] = True
         session['adminusername'] = admin['admin_username']
         msgsuccess = 'Logged in successfully !'
         return redirect(url_for('admindashboard'))
      else:
         msgdecline = 'Incorrect Username / Password !'
   return render_template('adminlogin.html', msgdecline = msgdecline)
  
  
  
@app.route('/customerregister', methods =['GET', 'POST'])
def customerregister():
   msgdecline = ''
   if request.method == 'POST' and 'cname' in request.form and 'cemail' in request.form and 'cpassword' in request.form and 'cconfirmpassword' in request.form :
      cname = request.form['cname']
      cemail = request.form['cemail']
      cpassword = request.form['cpassword']
      cconfirmpassword = request.form['cconfirmpassword']
      cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      cursor.execute('SELECT * FROM customers_details WHERE customer_email = % s', (cemail, ))
      user_registration = cursor.fetchone()
      if user_registration:
         msgdecline = 'Account already exists ! Try Login'
      elif cpassword != cconfirmpassword:
         msgdecline = 'Password did not match !'
      else:
         ts = time.time()
         timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
         cursor.execute('INSERT INTO customers_details VALUES (%s, % s, % s, % s, % s)', (None, cname, cemail, cpassword, timestamp, ))
         mysql.connection.commit()
         flash('You have successfully registered ! Try Login')
         try:
            mailmsg = Message('Customer Care Registry', sender = 'Registration Successful', recipients = ['{}', cemail])
            mailmsg.body = "Hello {},\nYou have successfully registered on Customer Care Registry".format(cname)
            mail.send(mailmsg)
         except:
            pass
         return redirect(url_for('customerlogin'))
   elif request.method == 'POST':
      msgdecline = 'Please fill out the form !'
   return render_template('customerregister.html', msgdecline = msgdecline)



@app.route('/agentregister', methods =['GET', 'POST'])
def agentregister():
   if not session.get("adminusername"):
      return redirect("/adminlogin")
   else:
      msgdecline = ''
      if request.method == 'POST' and 'aname' in request.form and 'aemail' in request.form and 'ausername' in request.form and 'apassword' in request.form and 'aconfirmpassword' in request.form :
         aname = request.form['aname']
         aemail = request.form['aemail']
         ausername = request.form['ausername']
         apassword = request.form['apassword']
         aconfirmpassword = request.form['aconfirmpassword']
         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('SELECT * FROM agent_information WHERE agent_email = % s', (aemail, ))
         agent_information = cursor.fetchone()
         if agent_information:
            msgdecline = 'Account already exists ! Try Login'
         else:
            ts = time.time()
            timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('INSERT INTO agent_information VALUES (%s, % s, % s, % s, % s, % s)', (None, aname, aemail, ausername, apassword, timestamp,))
            mysql.connection.commit()
            flash('Agent Has been successfully registered !')
            try:
               mailmsg = Message('Customer Care Registry', sender = 'Registration Successful', recipients = ['{}', aemail])
               mailmsg.body = "Hello, You have been Successfully Registered as Agent"
               mail.send(mailmsg)
            except:
               pass
            return redirect(url_for('agentlogin'))
      elif request.method == 'POST':
         msg = 'Please fill out the form !'
   return render_template('agentregister.html', msgdecline = msgdecline)



@app.route('/welcome', methods =['GET', 'POST'])
def welcome():
   if not session.get("cemail"):
      return redirect("/customerlogin")
   else:
      msgsuccess = ''
      msgdecline = ''
      cmail = session['cemail']
      mycursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      mycursor.execute('SELECT * FROM complaint_details WHERE customer_email = %s ORDER BY timestamp DESC', (cmail,))
      data = mycursor.fetchall()
      mycursor.execute('SELECT customer_name FROM customers_details WHERE customer_email = %s', (cmail,))
      cname = mycursor.fetchone()
      if request.method == 'POST' and 'name' in request.form and 'email' in request.form and 'category' in request.form and 'subject' in request.form and 'description' in request.form :
         name = request.form['name']
         email = request.form['email']
         category = request.form['category']
         subject = request.form['subject']
         description = request.form['description']
         ticketno = random.randint(100000, 999999)
         ts = time.time()
         timestamp = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('INSERT INTO complaint_details VALUES (%s, % s, % s, % s, % s, % s, % s, % s, % s )', (ticketno, name, email, category, subject, description, timestamp , "pending" , "pending" , ))
         mysql.connection.commit()
         try:
            mailmsg = Message('Customer Care Registry', sender = 'Request Received', recipients = ['{}', email])
            mailmsg.body = "Hello {},\n\nThanks for contacting Customer Care Registry\nWe have received your complain\nYour Ticket Number: {}\nCategory: {}\nSubject: {}\nDescription: {}\n\nWe strive to provide excellent service, and will respond to your request as soon as possible.".format(name, ticketno, category, subject, description)
            mail.send(mailmsg)
         except: 
            pass
         flash ('Your complaint is successfully submitted !')
         return redirect(url_for('welcome'))
      elif request.method == 'POST':
         msgdecline = 'Please fill out the form !'
   return render_template('welcome.html', msgsuccess = msgsuccess, data=data, cname=cname)
   


@app.route('/agentdashboard', methods =['GET', 'POST'])
def agentdashboard():
   if not session.get("aemail"):
      return redirect("/agentlogin")
   else:
      msg = ''
      aemail = session['aemail']
      mycursor1 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      mycursor1.execute('SELECT agent_name FROM agent_information WHERE agent_email = %s', (aemail, ))
      agent = mycursor1.fetchone()
      
      for x in agent:
         agent_name = agent[x]
         
      mycursor2 = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      mycursor2.execute('SELECT * FROM complaint_details WHERE agent_name = %s ORDER BY timestamp DESC', (agent_name, ))
      data = mycursor2.fetchall()
      if request.method == 'POST' and 'status' in request.form :
         status = request.form['status']
         ticketno = request.form['ticketno']
         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('UPDATE complaint_details SET status = %s WHERE ticket_no = %s', (status, ticketno,) )
         mysql.connection.commit()
         msg = 'Your complaint is successfully solved !'
         
         mailcursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         mailcursor.execute('SELECT customer_email FROM complaint_details WHERE ticket_no = %s', (ticketno,) )
         customer_mail = mailcursor.fetchone()
         
         for x in customer_mail:
            cemail = customer_mail[x]
            
         try:
            mailmsg = Message('Customer Care Registry', sender = 'Your Ticket Status', recipients = ['{}', cemail])
            mailmsg.body = "Hello, \nYour complaint has been successfully solved\nYour Ticket Number: {}".format(ticketno)
            mail.send(mailmsg)
         except:
            pass
         return redirect(url_for('agentdashboard'))
      elif request.method == 'POST':
         msg = 'Please fill out the form !'
   return render_template('agentdashboard.html', msg = msg, data=data, agent_name=agent_name)



@app.route('/admindashboard', methods =['GET', 'POST'])
def admindashboard():
   if not session.get("adminusername"):
      return redirect("/adminlogin")
   else:
      msg = ''
      mycursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
      mycursor.execute('SELECT * FROM complaint_details ORDER BY timestamp DESC')
      data = mycursor.fetchall()
      mycursor.execute('SELECT * FROM agent_information')
      agent = mycursor.fetchall()
      mycursor.execute('SELECT COUNT(status) AS pending FROM complaint_details WHERE status = %s', ("pending",))
      pending = mycursor.fetchall()
      mycursor.execute('SELECT COUNT(status) AS assigned FROM complaint_details WHERE status = %s', ("Agent Assigned",))
      assigned = mycursor.fetchall()
      mycursor.execute('SELECT COUNT(status) AS completed FROM complaint_details WHERE status = %s', ("Closed",))
      completed = mycursor.fetchall()
      if request.method == 'POST' and 'agentassign' in request.form :
         agentassign = request.form['agentassign']
         adminusername = request.form['adminusername']
         ticketno = request.form['ticketno']
         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('UPDATE complaint_details SET agent_name = %s WHERE ticket_no = %s', (agentassign, ticketno,) )
         cursor.execute('UPDATE complaint_details SET status = %s WHERE ticket_no = %s', ("Agent Assigned", ticketno,) )
         mysql.connection.commit()
         msg = 'Your complaint is Assigned to Agent !'
         
         mailcursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         mailcursor.execute('SELECT customer_email FROM complaint_details WHERE ticket_no = %s', (ticketno,) )
         customer_mail = mailcursor.fetchone()
         
         for x in customer_mail:
            cemail = customer_mail[x]
         
         try:
            mailmsg = Message('Customer Care Registry', sender = 'Agent Assigned', recipients = ['{}', cemail])
            mailmsg.body = "Hello,\nWe have received your complaint and agent {} has been Successfully Assigned\nYour Ticket Number: {}\n\nYou will be notified when your complain will be solved.".format(agentassign, ticketno)
            mail.send(mailmsg)
         except:
            pass
         return redirect(url_for('admindashboard'))
      elif request.method == 'POST':
         msg = 'Please fill out the form !'
   return render_template('admindashboard.html', msg = msg, data=data, agent=agent, pending=pending, assigned=assigned, completed=completed)



@app.route('/adminanalytics')
def adminanalytics():
   mycursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
   mycursor.execute('SELECT COUNT(agent_name) AS JenTile FROM complaint_details WHERE agent_name = %s', ("Jen Tile",))
   JenTile = mycursor.fetchall()
   mycursor.execute('SELECT COUNT(agent_name) AS AllieGrater FROM complaint_details WHERE agent_name = %s', ("Allie Grater",))
   AllieGrater = mycursor.fetchall()
   mycursor.execute('SELECT COUNT(agent_name) AS RaySin FROM complaint_details WHERE agent_name = %s', ("Ray Sin",))
   RaySin = mycursor.fetchall()
   mycursor.execute('SELECT COUNT(category) AS Category1 FROM complaint_details WHERE category = %s', ("Product Exchange or Return",))
   category1 = mycursor.fetchall()
   mycursor.execute('SELECT COUNT(category) AS Category2 FROM complaint_details WHERE category = %s', ("Product Out of Stock",))
   category2 = mycursor.fetchall()
   mycursor.execute('SELECT COUNT(category) AS Category3 FROM complaint_details WHERE category = %s', ("Payments & Transactions",))
   category3 = mycursor.fetchall()
   mycursor.execute('SELECT COUNT(category) AS Category4 FROM complaint_details WHERE category = %s', ("Product Delivery",))
   category4 = mycursor.fetchall()
   mycursor.execute('SELECT COUNT(category) AS Category5 FROM complaint_details WHERE category = %s', ("Other",))
   category5 = mycursor.fetchall()
   print(category1)
   return render_template('adminanalytics.html', JenTile=JenTile, AllieGrater=AllieGrater, RaySin=RaySin, category1=category1, category2=category2, category3=category3, category4=category4, category5=category5)



@app.route('/customerforgotpassword', methods =['GET', 'POST'])
def customerforgotpassword():
      msgdecline = ''
      if request.method == 'POST' and 'customerforgotemail' in request.form :
         forgotemail = request.form['customerforgotemail']
         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('SELECT * FROM customers_details WHERE customer_email = % s', (forgotemail, ))
         customers_details = cursor.fetchone()
         if customers_details:
            session['customerforgotemail'] = forgotemail
            otp = random.randint(1000, 9999)
            session['otp'] = otp
            try:
               mailmsg = Message('Customer Care Registry', sender = 'Forgot Password', recipients = ['{}', forgotemail])
               mailmsg.body = "Hello, \nYour OTP is: {}\nDo not share this OTP to anyone \nUse this OTP to reset your password.".format(otp)
               mailmsg.subject = 'Forgot Passowrd'
               mail.send(mailmsg)
               flash('OTP has been sent to your email')
               return redirect(url_for('enterotp'))
            except:
               msgdecline = 'Oops! Something went wrong! Email not sent'
         else:
            msgdecline = 'This email is not registered!'
      return render_template('customerforgotpassword.html', msgdecline = msgdecline)
   
   
   
@app.route('/agentforgotpassword', methods =['GET', 'POST'])
def agentforgotpassword():
      msgdecline = ''
      if request.method == 'POST' and 'agentforgotemail' in request.form :
         forgotemail = request.form['agentforgotemail']
         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('SELECT * FROM agent_information WHERE agent_email = % s', (forgotemail, ))
         agent_information = cursor.fetchone()
         if agent_information:
            session['agentforgotemail'] = forgotemail
            otp = random.randint(1000, 9999)
            session['otp'] = otp
            try:
               mailmsg = Message('Customer Care Registry', sender = 'Forgot Password', recipients = ['{}', forgotemail])
               mailmsg.body = "Hello, \nYour OTP is: {}\nDo not share this OTP to anyone \nUse this OTP to reset your password.".format(otp)
               mail.send(mailmsg)
               flash('OTP has been sent to your email')
               return redirect(url_for('enterotp'))
            except:
               msgdecline = 'Oops! Something went wrong! Email not sent'
         else:
            msgdecline = 'This email is not registered!'
      return render_template('agentforgotpassword.html', msgdecline = msgdecline)
   
   
   
@app.route('/adminforgotpassword', methods =['GET', 'POST'])
def adminforgotpassword():
      msgdecline = ''
      if request.method == 'POST' and 'adminforgotemail' in request.form :
         forgotemail = request.form['adminforgotemail']
         cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
         cursor.execute('SELECT * FROM admin_details WHERE admin_email = % s', (forgotemail, ))
         admin_details = cursor.fetchone()
         if admin_details:
            session['adminforgotemail'] = forgotemail
            otp = random.randint(1000, 9999)
            session['otp'] = otp
            try:
               mailmsg = Message('Customer Care Registry', sender = 'Forgot Password', recipients = ['{}', forgotemail])
               mailmsg.body = "Hello, \nYour OTP is: {}\nDo not share this OTP to anyone \nUse this OTP to reset your password.".format(otp)
               mail.send(mailmsg)
               flash('OTP has been sent to your email')
               return redirect(url_for('enterotp'))
            except:
               msgdecline = 'Oops! Something went wrong! Email not sent'
         else:
            msgdecline = 'This email is not registered!'
      return render_template('adminforgotpassword.html', msgdecline = msgdecline)
   


@app.route('/enterotp', methods =['GET', 'POST'])
def enterotp():
      msgdecline = ''
      if request.method == 'POST' and 'otp' in request.form :
         otp = int(request.form['otp'])
         if int(session['otp']) == otp:
            msgsuccess = 'success'
            return redirect(url_for('changepassword')) 
         else:
            msgdecline = 'You have entered wrong OTP'  
      elif request.method == 'POST':
         msg = 'Please fill out the form !'
      return render_template('enterotp.html', msgdecline = msgdecline)



@app.route('/changepassword', methods =['GET', 'POST'])
def changepassword():
      msgdecline = ''
      if request.method == 'POST' and 'newpassword' in request.form and 'confirmnewpassword' in request.form:
         newpassword = request.form['newpassword']
         confirmnewpassword = request.form['confirmnewpassword']
         if newpassword == confirmnewpassword:
            cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
            if session.get("customerforgotemail"):
               cursor.execute('UPDATE customers_details SET customer_password = %s WHERE customer_email = %s', (newpassword, session['customerforgotemail'],) )
               mysql.connection.commit()
               flash('Your password changed Successful! Try Login')
               return redirect(url_for('customerlogin'))
            elif session.get("agentforgotemail"):
               cursor.execute('UPDATE agent_information SET agent_password = %s WHERE agent_email = %s', (newpassword, session['agentforgotemail'],) )
               mysql.connection.commit()
               flash('Your password changed Successful! Try Login')
               return redirect(url_for('agentlogin'))
            elif session.get("adminforgotemail"):
               cursor.execute('UPDATE admin_details SET admin_password = %s WHERE admin_email = %s', (newpassword, 'admin@xyz',) )
               mysql.connection.commit()
               flash('Password changed Successful! Try Login')
               return redirect(url_for('adminlogin'))
            else:
               msgdecline = 'Incorrect details'
         else:
            msgdecline = 'Password Did Not Match!'    
      elif request.method == 'POST':
         msgdecline = 'Please fill out the form !'
      return render_template('changepassword.html', msgdecline = msgdecline)



@app.route('/logout')
def logout():
   session.pop('loggedin', None)
   session.pop('cemail', None)
   session.pop('aemail', None)
   session.pop('adminusername', None)
   return redirect(url_for('index'))



@app.route('/offline.html')
def offline():
    return app.send_static_file('offline.html')



@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')



@app.errorhandler(404)
def invalid_route(e):
   return render_template('404.html')



if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True,port = 8080)
