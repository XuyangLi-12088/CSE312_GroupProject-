from flask import Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
import functools

mongo_client = MongoClient("mongo")
db = mongo_client["CSE312_Final_Project"] 

app = Flask(__name__)

app.config['SECRET_KEY'] = 'c032ce37b8b5cb5f4f50e2736bae275f'

@app.route('/')
def home():
    return render_template('shopping_sign_out.html')

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    if (request.method == "POST"):
        error = ''
        # Get entered username and password
        get_username = request.form["username"]
        get_password = request.form["password"]
        print(get_username)
        print(get_password)

        # Check if the entered username and password are between 6 - 20 characters
        if (len(get_username) < 6 or len(get_username) > 20):
            error = "Entered username and password must between 6 - 20 characters"
            #return render_template("sign_up.html")
        elif (len(get_password) < 6 or len(get_password) > 20):
            error = "Entered username and password must between 6 - 20 characters"
            #return render_template("sign_up.html")

        # Check if the entered username exist or not

        # Store username and password into the database


        flash(error)


    # print(request.method)
    # print(request.path)
    # print(request.form)
    return render_template("sign_up.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    #print(request.method)
    #print(request.path)
    #print(request.form)
    #print(request.form["username"])
    #print(request.form["password"])
    return render_template("login.html")

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




# command that use flask run the server
    # flask --app project_server.py --debug run

# command that use docker run the server
    # • To run your app [and database]
        # • docker-compose up
    # • To run in detached mode
        # • docker-compose up -d
    # • To rebuild and restart the containers
        # • docker-compose up --build --force-recreate
    # • To restart the containers without rebuilding
        # • docker-compose restart
