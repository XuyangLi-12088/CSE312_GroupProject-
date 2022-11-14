from flask import Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
import functools

mongo_client = MongoClient("mongo")
db = mongo_client["CSE312_Final_Project"] 

users_collection = db["users"]

# username contians each user's username, password contians each user's password
#users_collection.insert_one({'username': "", 'password': ""})

app = Flask(__name__)

app.config['SECRET_KEY'] = 'c032ce37b8b5cb5f4f50e2736bae275f'

# Home Page - Shopping Web Page When User not signed in
@app.route('/', methods=["GET", "POST"])
def home():
    print("Request form: " + str(request.form), flush = True)
    print("Request method: " + str(request.method), flush = True)
    print("Request path: " + str(request.path), flush = True)

    return render_template('shopping_sign_out.html')

# Shopping Web Page When User loged in
@app.route('/signed_in')
def signed_in():
    return render_template('shopping_sign_in.html')

# User Sign Up Web Page
@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():

    print("Request form: " + str(request.form), flush = True)
    print("Request method: " + str(request.method), flush = True)
    print("Request path: " + str(request.path), flush = True)

    if (request.method == "POST"):
        error = ''
        # Get entered username and password
        get_username = request.form["username"]
        get_password = request.form["password"]
        print("sign up username: " + get_username, flush = True)
        print("sign up password: " + get_password, flush = True)

        # Check if the entered username and password are between 6 - 20 characters
        if (len(get_username) < 6 or len(get_username) > 20):
            error = "Entered username and password must between 6 - 20 characters"
            flash(error)
            return render_template("sign_up.html")
        elif (len(get_password) < 6 or len(get_password) > 20):
            error = "Entered username and password must between 6 - 20 characters"
            flash(error)
            return render_template("sign_up.html")

        # Check if the entered username exist or not
        check_exist = list(users_collection.find({"username": get_username}, {"_id": 0}))
        print("users in database: " + str(check_exist), flush = True)

        if (len(check_exist) == 0):
            # username not exists
            # Store username and password into the database
            users_collection.insert_one({"username": get_username, "password": generate_password_hash(get_password)})
            return redirect(url_for("login"))

        else:
            # username already exists
            error = "Username already exists, Plase choose another username"
            flash(error)
            return render_template("sign_up.html")

    return render_template("sign_up.html")

# User Log in Web Page
@app.route("/login", methods=["GET", "POST"])
def login():

    print("Request form: " + str(request.form), flush = True)
    print("Request method: " + str(request.method), flush = True)
    print("Request path: " + str(request.path), flush = True)

    if (request.method == "POST"):
        error = ''
        # get the login username and password
        get_login_username = request.form["username"]
        get_login_password = request.form["password"]
        print("login username: " + get_login_username, flush = True)
        print("login password: " + get_login_password, flush = True)

        # check if username is in the database
        check_exist = list(users_collection.find({"username": get_login_username}, {"_id": 0}))
        print("users in database: " + str(check_exist), flush = True)

        if (len(check_exist) == 0):
            # username does not exist in the database
            error = "Username does not exist!"
            flash(error)
            return render_template("login.html")
        else:
            # username exist in the database
            # get the hashed password
            if (check_password_hash(check_exist[0]['password'], get_login_password) == True):
                # password matches
                return redirect(url_for("signed_in"))
            else:
                error = "Wrong Password, Please try again!"
                flash(error)
                return render_template("login.html")

    return render_template("login.html")

# User Post Web Page
@app.route("/post", methods=["GET", "POST"])
def post():
    #if (request.method == "POST"):

    #print(request.method)
    #print(request.path)
    #print(request.form)
    #print(request.form["item_name"])
    #print(request.form["item_description"])
    #print(request.files["item_images"])
    #print(request.form["item_price"])
    return render_template("post.html")


if __name__ == '__main__':
    app.run(host = "0.0.0.0", port = 8080, debug = True)







# <----------------Helper Commands--------------------->

# command that use flask run the server
    # flask --app auth.py --debug run

# command that use docker run the server
    # • To run your app [and database]
        # • docker-compose up
    # • To run in detached mode
        # • docker-compose up -d
    # • To rebuild and restart the containers
        # • docker-compose up --build --force-recreate
    # • To restart the containers without rebuilding
        # • docker-compose restart

# <--------------------------------------------------->
