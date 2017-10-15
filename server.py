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
    if 'loginID' not in session:
        session['loginID'] = False
    if 'loginName' not in session:
        session['loginName'] = ''
    if 'subWallID' not in session:
        session['subWallID'] = '1'
    if 'subWallName' not in session:
        session['subWallName'] = 'main'
    
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
    # print currentUser
    if currentUser:
        # flash("Login Successful")
        session['loginID'] = currentUser[0]['id']
        session['loginName'] = currentUser[0]['first_name']
        session['subWallID'] = 1
        # print session['loginID']
        # print session['loginName']
    else:
        flash("Password Entered Does Not Match Account")
        return redirect('/')
    return redirect('/wall')

@app.route('/logout', methods=['POST'])
def userlogout():
    session['loginID'] = False
    return redirect('/')

@app.route('/wall')
def wall():
    print '@',session['subWallID']
    getPostData = {'wallID':session['subWallID']}
    getPostsQuery = "SELECT first_name, message, users.id, messages.id AS msgID, messages.created_at FROM users JOIN messages on user_id = users.id WHERE subwall_id = :wallID;"
    allPosts = mysql.query_db(getPostsQuery, getPostData)
    # getCommentsQuery = "SELECT * FROM comments"
    getCommentsQuery = "SELECT message_id, user_id, comment, first_name, comments.created_at FROM users JOIN comments ON user_id = users.id ORDER BY comments.created_at;"
    allComments = mysql.query_db(getCommentsQuery)
    # print allComments
    # print allPosts
    getWallNameData = {'subWallID': session['subWallID']}
    getWallNameQuery = "SELECT * FROM subwall WHERE subwall.id = :subWallID"
    currentWallInfo = mysql.query_db(getWallNameQuery, getWallNameData)
    print 'currentWallInfo', currentWallInfo
    session['subWallName'] = currentWallInfo[0]['name']
    return render_template('wall.html', allPosts = allPosts, allComments = allComments)

@app.route('/wallpost', methods=['POST'])
def wallpost():
    postMessage = request.form['postMessage']
    inputMessageData = {'userID': session['loginID'],'message':postMessage}
    inputMessageQuery = "INSERT INTO `wallFlask`.`messages` (`user_id`, `message`, `created_at`, `updated_at`) VALUES (:userID, :message, NOW(), NOW());"
    mysql.query_db(inputMessageQuery,inputMessageData)
    return redirect('/wall')

@app.route('/searchSubWall', methods=['POST'])
def searchWall():
    wallSearchInput = request.form['subWall']
    wallSearchInputData = {'searchTerm': wallSearchInput}
    wallSearchQuery = "SELECT * FROM subwall WHERE subwall.name = :searchTerm;"
    wallSearchResult = mysql.query_db(wallSearchQuery,wallSearchInputData)
    print wallSearchResult
    if wallSearchResult:
        session['subWallID'] = wallSearchResult[0]['id']
        print session['subWallID']
        return redirect('/wall')
    else:
        subWallInsertQuery = "INSERT INTO `wallFlask`.`subwall` (`name`) VALUES (:searchTerm);"
        mysql.query_db(subWallInsertQuery,wallSearchInputData)
    return redirect('/wall')

@app.route('/postcomment', methods=['POST'])
def postcomment():
    commentMessage = request.form['commentMessage']
    messageID = request.form['msgID']
    commentMessageData = {'postID':messageID, 'userID':session['loginID'], 'commentMessage':commentMessage}
    commentInputQuery = "INSERT INTO `wallFlask`.`comments` (`message_id`, `user_id`, `comment`, `created_at`, `updated_at`) VALUES (:postID, :userID, :commentMessage, NOW(), NOW());"
    mysql.query_db(commentInputQuery,commentMessageData)
    return redirect('/wall')

app.run(debug=True)