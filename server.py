from flask import Flask, render_template, request, redirect, session, flash
import re, md5
# import the Connector function
from mysqlconnection import MySQLConnector
app = Flask(__name__)
app.secret_key = 'aSecret'
# connect and store the connection in "mysql" note that you pass the database name to the function
mysql = MySQLConnector(app, 'wallFlask')
# an example of running a query
# print mysql.query_db("SELECT * FROM friendList")
emailREGEX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')

@app.route('/')
def formPage():
    if 'loginStatus' not in session:
        session['loginStatus'] = False
    else:
        pass
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submitted():
    email = request.form['email']
    firstName = request.form['firstName']
    lastName = request.form['lastName']
    password = request.form['password']
    passwordC = request.form['passwordConfirm']
    hashedPassword = md5.new(password).hexdigest()
    state = True
    if len(email) < 1 or len(firstName) < 1 or len(lastName) < 1 or len(password) < 1 or len(passwordC) < 1:
        flash("All field must be filled")
        return redirect('/')
    if password != passwordC:
        flash("Password must match")
        state = False
    if len(password) < 9:
        flash("Password must be longer than 8 characters")
        state = False
    if not firstName.isalpha() or not lastName.isalpha():
        flash("First and last name must be all alphabets")
        state = False
    if not emailREGEX.match(email):
        flash("Invalid Email Address!")
        state = False
    if state == True:
        flash("Successfully Submitted")
        userData = {'email':email, 'first_name':firstName, 'last_name':lastName, 'password':hashedPassword}
        # insertQuery = "INSERT INTO `regAndLogin`.`users` (`email`, `first_name`, `last_name`, `password`) VALUES (:email, :first_name, :last_name, :password);"
        insertQuery = "INSERT INTO `wallFlask`.`users` (`first_name`, `last_name`, `email`, `password`, `created_at`) VALUES (:first_name, :last_name, :email, :password, NOW());"
        mysql.query_db(insertQuery, userData)
        print "Success"
        return redirect('/')
    else:
        print "Not Success"
        return redirect('/')

@app.route('/login', methods=['POST'])
def userlogin():
    email = request.form['email']
    password = request.form['password']
    hashedPassword = md5.new(password).hexdigest()
    userInputData = {'email':email, 'password':hashedPassword}
    loginQuery = "SELECT * FROM users WHERE email = :email AND password = :password"
    currentUser = mysql.query_db(loginQuery, userInputData)
    print currentUser
    if currentUser:
        flash("Login Successful")
        session['loginStatus'] = currentUser[0]['id']
        print session['loginStatus']
    else:
        flash("Password Entered Does Not Match Account")
    return redirect('/wall')

@app.route('/logout', methods=['POST'])
def userlogout():
    session['loginStatus'] = False
    return redirect('/')

@app.route('/wall')
def wall():
    return render_template('wall.html')

app.run(debug=True)