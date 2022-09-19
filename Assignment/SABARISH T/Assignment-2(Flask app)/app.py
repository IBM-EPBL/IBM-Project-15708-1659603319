from flask import Flask, render_template
app = Flask(__name__)


@app.route('/')
def index():
   return render_template('index.html')


@app.route('/about')
def about():
   return render_template('about.html')


@app.route('/customerlogin')
def customerlogin():
   return render_template('customerlogin.html')


@app.route('/customerregister')
def customerregister():
   return render_template('customerregister.html')




