from flask import Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import functools
import secrets
import hashlib
import os
from helper_function import escape_html

mongo_client = MongoClient("mongo")
db = mongo_client["CSE312_Final_Project"] 

# <----------------------- Create database in Here! ----------------------->
# Format of users_collection: 
# {
#   { "username": str(" "), 
#     "password": str(" "), 
#     "posts": List[{"post_id": "", "item_name": "", "item_description": "", "item_image": "", "item_price": ""}],
#     "purchases": List["post_id": "", "item_name": "", "item_description": "", "item_image": "", "item_price": ""}],
#     "auth_token": bytes(" ")
#   }
# }
users_collection = db["users"]
# Format of post_collection:
# {
#   { "post_id": "", "item_name": "", "item_description": "", "item_image": "", "item_price": ""}
#   { "post_id": "", "item_name": "", "item_description": "", "item_image": "", "item_price": ""}
# }
post_collection = db["posts"]

# Format of posts_id_collection:
# {
#   {"last_id": int(next_id)}
# }
posts_id_collection = db["users_id"]

# <----------------------- Create database in Here! ----------------------->

UPLOAD_FOLDER = 'static/uploads/'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg'}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'c032ce37b8b5cb5f4f50e2736bae275f'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def get_next_id():
    id_object = posts_id_collection.find_one({})
    if id_object:
        next_id = int(id_object['last_id']) + 1
        posts_id_collection.update_one({}, {'$set': {'last_id': next_id}})
        return next_id
    else:
        posts_id_collection.insert_one({'last_id': 1})
        return 1


# Home Page - Shopping Web Page When User not signed in
@app.route('/', methods=["GET", "POST"])
def home():
    print("Request form: " + str(request.form), flush = True)
    print("Request method: " + str(request.method), flush = True)
    print("Request path: " + str(request.path), flush = True)
    # posts = get all posts from database
    # update html: % for post in posts %}
    posts_list = list(post_collection.find({}, {"_id": 0}))

    return render_template('shopping_sign_out.html', posts_list = posts_list)


# Shopping Web Page When User loged in
@app.route('/signed_in')
def signed_in():
    # Check if "auth_token" exist in Cookie
    get_auth_token = request.cookies.get('auth_token')
    # if there is no auth_token set, redirect the user to login page
    if (get_auth_token == None):
        return redirect(url_for("login"))
    # if there is a auth_token set
    else:
        # hash the auth token that we got from the request
        sha256_auth_token = hashlib.sha256()
        sha256_auth_token.update(get_auth_token.encode())
        hashed_auth_token = sha256_auth_token.digest()
        # check if the hashed auth token exist in our database
        check_exist = list(users_collection.find({"auth_token": hashed_auth_token}, {"_id": 0}))
        if (len(check_exist) == 0):
            return redirect(url_for("login"))
        else:
            # update html template
            username = check_exist[0]['username']
            posts_list = list(post_collection.find({}, {"_id": 0}))

            return render_template('shopping_sign_in.html', current_user = username, posts_list = posts_list)


# User Sign Up Web Page
@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():

    print("Request form: " + str(request.form), flush = True)
    print("Request method: " + str(request.method), flush = True)
    print("Request path: " + str(request.path), flush = True)
    #print("Request header: " + str(request.headers), flush = True)

    if (request.method == "POST"):
        error = ''
        # Get entered username and password
        get_username = escape_html(request.form["username"])
        get_password = escape_html(request.form["password"])
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
        #print("users in database: " + str(check_exist), flush = True)

        if (len(check_exist) == 0):
            # username not exists
            # Store username and password into the database
            users_collection.insert_one({"username": get_username, "password": generate_password_hash(get_password), "posts": [], "purchases": []})
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
        get_login_username = escape_html(request.form["username"])
        get_login_password = escape_html(request.form["password"])
        print("login username: " + get_login_username, flush = True)
        print("login password: " + get_login_password, flush = True)

        # check if username is in the database
        check_exist = list(users_collection.find({"username": get_login_username}, {"_id": 0}))
        #print("users in database: " + str(check_exist), flush = True)

        if (len(check_exist) == 0):
            # username does not exist in the database
            error = "Username does not exist!"
            flash(error)
            return render_template("login.html")
        else:
            # username exist in the database
            # get username from database
            get_username = check_exist[0]["username"]
            # get the hashed password
            if (check_password_hash(check_exist[0]['password'], get_login_password) == True):
                # password matches
                # Generate a Authentication Token
                auth_token = secrets.token_hex(80)
                #print("Authentication Token: " + auth_token)
                # hash the auth_token using SHA256
                sha256_auth_token = hashlib.sha256()
                sha256_auth_token.update(auth_token.encode())
                hashed_auth_token = sha256_auth_token.digest()
                # add hashed auth_token into user's database
                users_collection.update_one({'username': get_login_username}, {"$set": {"auth_token" : hashed_auth_token}})
                resp = make_response(redirect(url_for("signed_in")))
                resp.set_cookie("auth_token", value = auth_token, max_age = 31536000, httponly = True)
                return resp
            else:
                error = "Wrong Password, Please try again!"
                flash(error)
                return render_template("login.html")

    return render_template("login.html")


# User Post Web Page
@app.route("/post", methods=["GET", "POST"])
#@login_required
def post():

    print(request.method, flush = True)
    print(request.path, flush = True)
    print(request.form, flush = True)

    if (request.method == "GET"):
        # Check if "auth_token" exist in Cookie
        get_auth_token = request.cookies.get('auth_token')
        # if there is no auth_token set, redirect the user to login page
        if (get_auth_token == None):
            return redirect(url_for("login"))
        # if there is a auth_token set
        else:
            # hash the auth token that we got from the request
            sha256_auth_token = hashlib.sha256()
            sha256_auth_token.update(get_auth_token.encode())
            hashed_auth_token = sha256_auth_token.digest()
            # check if the hashed auth token exist in our database
            check_exist = list(users_collection.find({"auth_token": hashed_auth_token}, {"_id": 0}))
            if (len(check_exist) == 0):
                return redirect(url_for("login"))
            else:
                # update html template
                username = check_exist[0]['username']
                return render_template('post.html', current_user = username)


    if (request.method == "POST"):
        # Check if "auth_token" exist in Cookie
        get_auth_token = request.cookies.get('auth_token')
        # if there is no auth_token set, redirect the user to login page
        if (get_auth_token == None):
            return redirect(url_for("login"))
        # if there is a auth_token set
        else:
            # hash the auth token that we got from the request
            sha256_auth_token = hashlib.sha256()
            sha256_auth_token.update(get_auth_token.encode())
            hashed_auth_token = sha256_auth_token.digest()
            # check if the hashed auth token exist in our database
            check_exist = list(users_collection.find({"auth_token": hashed_auth_token}, {"_id": 0}))
            if (len(check_exist) == 0):
                return redirect(url_for("login"))
            else:
                username = check_exist[0]['username']
                # get all inputs
                get_item_name = escape_html(request.form["item_name"])
                get_item_description = escape_html(request.form["item_description"])
                get_item_image = request.files["item_images"]
                get_item_price = escape_html(request.form["item_price"])
                print("Item_name: " + get_item_name, flush = True)
                print("Item_description: " + get_item_description, flush = True)
                print("Item_image: " + str(get_item_image), flush = True)
                print("Item_image_name: " + get_item_image.filename, flush=True)
                print("Item_price: " + get_item_price, flush = True)
                error = ''
                check_item_name = False
                check_item_description = False
                check_item_image = False
                check_item_price = False

                # check if all the inputs are vaild
                # set a limit to item name, item name must between 1 to 200 characters
                if (len(get_item_name) >= 1 and len(get_item_name) <= 200):
                    # "check_item_name = True" means input is a valid item name
                    check_item_name = True
                else:
                    error = "Invalid Item Name, Make sure item name is between 0 to 200 Characters"
                    flash(error)
                    return render_template("post.html", current_user = username)

                # set a limit to item description, item description must between 1 to 2000 characters
                if (len(get_item_description) >= 1 and len(get_item_description) <= 2000):
                    # "check_item_description = True" means input is a valid item description
                    check_item_description = True
                else:
                    error = "Invalid Item Description, Make sure item description is between 0 to 2000 Characters"
                    flash(error)
                    return render_template("post.html", current_user = username)

                # set a limit to item price, item price must between 1 to 100 characters
                if (len(get_item_price) >= 1 and len(get_item_price) <= 100):
                    # Make sure price input only contains numbers
                    # If all characters in item price are numbers
                    if (get_item_price.isnumeric() == True):
                        # set ".00" to the end of the price
                        get_item_price = get_item_price + ".00"
                        check_item_price = True
                    # Not all characteres in item price are numbers
                    else:
                        if ("." in get_item_price):
                            dot_index = get_item_price.find(".")
                            price_before_dot = get_item_price[0 : dot_index]
                            print("price_before_dot: " + price_before_dot, flush=True)
                            price_after_dot = get_item_price[dot_index + 1 :]
                            print("price_after_dot: " + price_after_dot, flush=True)
                            for character in price_before_dot:
                                if (character.isnumeric() == True):
                                    pass
                                else:
                                    error = "Invalid item price"
                                    flash(error)
                                    return render_template("post.html", current_user = username)

                            if (len(price_after_dot) == 2):
                                if (price_after_dot.isnumeric() == True):
                                    check_item_price = True
                                else:
                                    error = "Invalid item price"
                                    flash(error)
                                    return render_template("post.html", current_user = username)
                            elif (len(price_after_dot) == 1):
                                if (price_after_dot.isnumeric() == True):
                                    get_item_price = get_item_price + '0'
                                    check_item_price = True
                                else:
                                    error = "Invalid item price"
                                    flash(error)
                                    return render_template("post.html", current_user = username)
                            else:
                                error = "Invalid item price, make sure set the price to two decimal places"
                                flash(error)
                                return render_template("post.html", current_user = username)
                        else:
                            error = "Invalid item price"
                            flash(error)
                            return render_template("post.html", current_user = username)
                else:
                    error = "Invalid item price"
                    flash(error)
                    return render_template("post.html", current_user = username)

                # set a limit to item image, number of item images must be 1
                if (get_item_image.filename != ''):
                    image_split_list = get_item_image.filename.split(".")
                    if (image_split_list[1] in ALLOWED_EXTENSIONS):
                        # "check_item_image = True" means input is a valid item image
                        check_item_image = True
                        filename = secure_filename(get_item_image.filename)
                        get_item_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    else:
                        error = "Invalid Item Image, Make sure the type of the file is jpg or jpeg"
                        flash(error)
                        return render_template("post.html", current_user = username)
                else:
                    error = "Invalid Item Image, Make sure upload an image"
                    flash(error)
                    return render_template("post.html", current_user = username)

        # <-- All inputs are valid at this point -->
        # build current post informations
        post_content = {}
        post_content["post_id"] = get_next_id()
        post_content["item_name"] = get_item_name
        post_content["item_description"] = get_item_description
        post_content["item_image"] = filename
        post_content["item_price"] = get_item_price
        # Store all inputs into the post database
        post_collection.insert_one(post_content)
        print("post_collection: " + str(list(post_collection.find({}, {"_id": 0}))), flush=True)

        # Store all inputs into current user's database
        get_user_from_database = list(users_collection.find({"username": username}, {"_id": 0}))
        # get current user's "posts" list
        user_post_list = get_user_from_database[0]["posts"]
        user_post_list.append(post_content)
        users_collection.update_one({'username': username}, {"$set": {"posts" : user_post_list}})
        print("user_collection: " + str(list(users_collection.find({}, {"_id": 0}))), flush=True)

        return redirect(url_for("signed_in"))


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
