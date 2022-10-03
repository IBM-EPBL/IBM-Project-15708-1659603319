from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import re, random, smtplib, os, time, datetime
import ibm_db
from markupsafe import escape

conn = ibm_db.connect("DATABASE=bludb;HOSTNAME=21fecfd8-47b7-4937-840d-d791d0218660.bs2io90l08kqb1od8lcg.databases.appdomain.cloud;PORT=31864;SECURITY=SSL;SSLServerCertificate=DigiCertGlobalRootCA.crt;UID=rtp84701;PWD=DJ4gX1wChdTCGZPz",'','')
print(conn)
print("connection successful...")


app = Flask(__name__)
app.secret_key = '12345'


@app.route('/')
def index():
   return render_template('index.html')

@app.route('/profile')
def profile():
   return render_template('profile.html')


@app.route('/about')
def about():
   return render_template('about.html')


@app.route('/customerlogin', methods =['GET', 'POST'])
def customerlogin():
   msgdecline = ''
   if request.method == 'POST' and 'cemail' in request.form and 'cpassword' in request.form:
      cemail = request.form['cemail']
      cpassword = request.form['cpassword']
      sql =f"select * from users where cemail='{escape(cemail)}' and cpassword='{escape(cpassword)}'"
      stmt = ibm_db.exec_immediate(conn, sql)
      customers_details = ibm_db.fetch_both(stmt)

      
      if customers_details:
         session['loggedin'] = True
         session["cemail"]=escape(cemail)
         session["cpassword"]=escape(cpassword)
         msgsuccess = 'Logged in successfully !'
         return redirect("profile")
      else:
         msgdecline = 'Incorrect Email / Password !'
   return render_template('customerlogin.html', msgdecline = msgdecline)



@app.route('/customerregister',methods = ['POST', 'GET'])
def customerregister():
   if request.method == 'POST':
      try:
         cname = request.form['cname']
         cemail = request.form['cemail']
         cpassword = request.form['cpassword']
         cconfirmpassword = request.form['cconfirmpassword']

      
         insert_sql ="INSERT INTO users(cname,cemail,cpassword,cconfirmpassword)VALUES(?,?,?,?)"
         prep_stmt = ibm_db.prepare(conn,insert_sql)
         ibm_db.bind_param(prep_stmt,1,cname)
         ibm_db.bind_param(prep_stmt,2,cemail)
         ibm_db.bind_param(prep_stmt,3,cpassword)
         ibm_db.bind_param(prep_stmt,4,cconfirmpassword)
         ibm_db.execute(prep_stmt)
         flash("Register successfully","success")        
      except:
         flash("Error","danger")
      finally:
         return redirect(url_for("index"))
         con.close()
   return render_template('customerregister.html')





if __name__ == '__main__':
    app.run(host='0.0.0.0', debug = True,port = 4000)

