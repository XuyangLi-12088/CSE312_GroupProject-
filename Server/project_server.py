from flask import Flask, Blueprint, flash, g, redirect, render_template, request, session, url_for, make_response
from flask_socketio import SocketIO, send, emit
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
import functools
import secrets
import hashlib
import os
import time
from helper_function import escape_html

mongo_client = MongoClient("mongo")
db = mongo_client["CSE312_Final_Project"] 

# <----------------------- Create database in Here! ----------------------->
# Format of users_collection: 
# {
#   { "username": str(" "), 
#     "password": str(" "), 
#     "posts": List[{"post_id": "", "item_name": "", "item_description": "", "item_image": "", "item_price": ""}],
#     "auctions": List[{"auction_id": "", "auction_item_name": "", "auction_item_description": "", "auction_item_image": "", "auction_current_price": "", "highest_bid_user": "", "auction_end_time": ""}],
#     "purchases": List["post_id": "", "item_name": "", "item_description": "", "item_image": "", "item_price": ""}],
#     "shopping_cart": List["post_id": "", "item_name": "", "item_description": "", "item_image": "", "item_price": ""}]
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

# Format of auction_collection:
# {
#   { "auction_id": "", "item_name": "", "item_description": "", "item_image": "", "auction_current_price": "", "highest_bid_user": "", "auction_end_time": ""}
#   { "auction_id": "", "item_name": "", "item_description": "", "item_image": "", "auction_current_price": "", "highest_bid_user": "", "auction_end_time": ""}
# }
auction_collection = db["auctions"]

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
socketio = SocketIO(app, cors_allowed_origins="*")

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
    
    # get all posts from posts database
    posts_list = list(post_collection.find({}, {"_id": 0}))
    # get all auctions from auctions database
    auctions_list = list(auction_collection.find({}, {"_id": 0}))

    return render_template('shopping_sign_out.html', posts_list = posts_list, auctions_list = auctions_list)


# Shopping Web Page When User loged in
@app.route('/signed_in', methods=["GET", "POST"])
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
            # get all posts from posts database
            posts_list = list(post_collection.find({}, {"_id": 0}))
            # get all auctions from auctions database
            auctions_list = list(auction_collection.find({}, {"_id": 0}))

            return render_template('shopping_sign_in.html', current_user = username, posts_list = posts_list, auctions_list = auctions_list)


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
            users_collection.insert_one({"username": get_username, "password": generate_password_hash(get_password), "posts": [], "auctions": [], "purchases": [], "shopping_cart": []})
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
                session['auth_token'] = auth_token
                return resp
            else:
                error = "Wrong Password, Please try again!"
                flash(error)
                return render_template("login.html")

    return render_template("login.html")


# User Post Web Page
@app.route("/post", methods=["GET", "POST"])
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


# User Account Web Page
@app.route("/account", methods=["GET", "POST"])
def account():
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
            return render_template('account.html', current_user = username)


# User Post History Web Page
@app.route("/post_history", methods=["GET", "POST"])
def post_history():
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
                # get all posts history from current user
                user_post_list = check_exist[0]["posts"]
                print("user's post list: " + str(user_post_list), flush=True)
                # get all auction history from current user
                user_auction_list = check_exist[0]["auctions"]
                print("user's auction list: " + str(user_auction_list), flush=True)
                return render_template('post_history.html', current_user = username, posts_list = user_post_list, auctions_list = user_auction_list)

    elif(request.method == "POST"):
        print(request.method, flush = True)
        print(request.path, flush = True)
        print(request.form, flush = True)
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
                if (request.form.get('post_id') != None):
                    # update html template
                    username = check_exist[0]['username']
                    # get the remove post id
                    remove_post_id = request.form['post_id']
                    # remove post from post_collection database
                    post_collection.delete_one({'post_id': int(remove_post_id)})
                    print("new post collection: " + str(list(post_collection.find({}, {"_id": 0}))), flush=True)
                    # remove post from users_collection database
                    # get the current user posts list
                    user_post_list = check_exist[0]["posts"]
                    # delete the remove post from user_post_list
                    for num in range(len(user_post_list)):
                        if (user_post_list[num]['post_id'] == int(remove_post_id)):
                            del user_post_list[num]
                            break
                    print("new user's post list: " + str(user_post_list), flush=True)
                    # update user's posts list in users_collection
                    users_collection.update_one({'username': username}, {"$set": {"posts" : user_post_list}})

                    # get current posts list from post_collection
                    posts_list = list(post_collection.find({}, {"_id": 0}))

                    # get current auction list from auction_collection
                    auctions_list = list(auction_collection.find({}, {"_id": 0}))

                    return render_template('shopping_sign_in.html', current_user = username, posts_list = posts_list, auctions_list = auctions_list)

                elif (request.form.get('auction_id') != None):
                    # update html template
                    username = check_exist[0]['username']
                    # get the remove auction id
                    remove_auction_id = request.form['auction_id']
                    # remove auction from auction_collection database
                    auction_collection.delete_one({'auction_id': int(remove_auction_id)})
                    print("new auction collection: " + str(list(auction_collection.find({}, {"_id": 0}))), flush=True)
                    # remove auction from users_collection database
                    # get the current user auction list
                    user_auction_list = check_exist[0]["auctions"]
                    # delete the remove auction from user_auction_list
                    for num in range(len(user_auction_list)):
                        if (user_auction_list[num]['auction_id'] == int(remove_auction_id)):
                            del user_auction_list[num]
                            break
                    print("new user's auction list: " + str(user_auction_list), flush=True)
                    # update user's posts list in users_collection
                    users_collection.update_one({'username': username}, {"$set": {"auctions" : user_auction_list}})

                    # get current posts list from post_collection
                    posts_list = list(post_collection.find({}, {"_id": 0}))

                    # get current auction list from auction_collection
                    auctions_list = list(auction_collection.find({}, {"_id": 0}))

                    return render_template('shopping_sign_in.html', current_user = username, posts_list = posts_list, auctions_list = auctions_list)



# Shopping Cart Web Page When User loged in
@app.route('/shop_cart', methods=["GET", "POST"])
def shopping_cart():
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
                shopping_cart_list = check_exist[0]['shopping_cart']

                return render_template('shopping_cart.html', current_user = username, shopping_cart_list = shopping_cart_list)

    elif (request.method == "POST"):
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
            print("current_user: " + str(check_exist))
            if (len(check_exist) == 0):
                return redirect(url_for("login"))
            else:
                # add the post into current user's shopping cart
                if (request.form.get('add_to_cart_post_id') != None):
                    # get current user's username
                    username = check_exist[0]['username']
                    # get the Post id for current item (Add To Cart)
                    post_id_for_cart = request.form['add_to_cart_post_id']
                    # get current users shopping cart list from database
                    shopping_cart_list = check_exist[0]["shopping_cart"]
                    # check if the current item already exist in user's shopping cart list
                    for item in shopping_cart_list:
                        if (item['post_id'] == int(post_id_for_cart)):
                            # calculate the total price in current user's shopping cart
                            total_price = 0
                            for post in shopping_cart_list:
                                total_price += float(post["item_price"])
                            return render_template('shopping_cart.html', current_user = username, shopping_cart_list = shopping_cart_list, total_price = total_price)
                        else:
                            pass
                    # get the Post by post id from post_collection 
                    add_to_cart_post = list(post_collection.find({"post_id": int(post_id_for_cart)}, {"_id": 0}))[0]
                    # add the Post into current user's shopping cart list
                    shopping_cart_list.append(add_to_cart_post)
                    # update current user's shopping cart list
                    users_collection.update_one({'username': username}, {"$set": {"shopping_cart" : shopping_cart_list}})

                    # calculate the total price in current user's shopping cart
                    total_price = 0
                    for post in shopping_cart_list:
                        total_price += float(post["item_price"])

                    return render_template('shopping_cart.html', current_user = username, shopping_cart_list = shopping_cart_list, total_price = total_price)

                # remove post from current user's shopping cart
                elif (request.form.get('remove_post_id') != None):
                    # get current user's username
                    username = check_exist[0]['username']
                    # get the Post id for current item (Remove Item From Cart)
                    post_id_for_cart = request.form['remove_post_id']
                    # get current users shopping cart list from database
                    shopping_cart_list = check_exist[0]["shopping_cart"]
                    # Remove the item from current user's shopping cart list
                    for num in range(len(shopping_cart_list)):
                        if (shopping_cart_list[num]['post_id'] == int(post_id_for_cart)):
                            del shopping_cart_list[num]
                            break
                    # update user's shopping cart list in users_collection
                    users_collection.update_one({'username': username}, {"$set": {"shopping_cart" : shopping_cart_list}})

                    # calculate the total price in current user's shopping cart
                    total_price = 0
                    for post in shopping_cart_list:
                        total_price += float(post["item_price"])

                    return render_template('shopping_cart.html', current_user = username, shopping_cart_list = shopping_cart_list, total_price = total_price)
                
                # Purchase all Items from current user's shopping cart
                elif (request.form.get('purchase_all') != None):
                    # get current user's username
                    username = check_exist[0]['username']
                    # get current user's shopping cart list from database
                    shopping_cart_list = check_exist[0]["shopping_cart"]
                    # get current user's "purchases" list from database
                    purchases_list = check_exist[0]["purchases"]
                    # add all items in current user's shopping cart list into current user's "purchases" list in database
                    for item in shopping_cart_list:
                        purchases_list.append(item)
                        # delete all cart items from post_collection
                        post_collection.delete_one({'post_id': int(item['post_id'])})

                    # clear current user's shopping cart list
                    shopping_cart_list = []
                    # update current user's shopping cart list and "purchases" list in database
                    users_collection.update_one({'username': username}, {"$set": {"shopping_cart" : shopping_cart_list}})
                    users_collection.update_one({'username': username}, {"$set": {"purchases" : purchases_list}})

                    # set total price to 0
                    total_price = 0

                    return render_template('shopping_cart.html', current_user = username, shopping_cart_list = shopping_cart_list, total_price = total_price)



# Purchases history Web Page When User loged in
@app.route('/purchase_history', methods=["GET", "POST"])
def purchase_history():
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
                purchases_list = check_exist[0]['purchases']

                return render_template('purchase_history.html', current_user = username, purchases_list = purchases_list)


# Auction Web Page When User loged in
@app.route('/auction', methods=["GET", "POST"])
def auction():
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
                return render_template('auction.html', current_user = username)

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
                get_item_price = escape_html(request.form["auction_price"])
                get_end_time = escape_html(request.form["auction_end_time"])
                print("Item_name: " + get_item_name, flush = True)
                print("Item_description: " + get_item_description, flush = True)
                print("Item_image: " + str(get_item_image), flush = True)
                print("Item_image_name: " + get_item_image.filename, flush = True)
                print("Auction_price: " + get_item_price, flush = True)
                print("Auction_End_Time: " + get_end_time, flush = True)
                error = ''

                # check if all the inputs are vaild
                # set a limit to item name, item name must between 1 to 200 characters
                if (len(get_item_name) >= 1 and len(get_item_name) <= 200):
                    pass
                else:
                    error = "Invalid Item Name, Make sure item name is between 0 to 200 Characters"
                    flash(error)
                    return render_template("auction.html", current_user = username)

                # set a limit to item description, item description must between 1 to 2000 characters
                if (len(get_item_description) >= 1 and len(get_item_description) <= 2000):
                    pass
                else:
                    error = "Invalid Item Description, Make sure item description is between 0 to 2000 Characters"
                    flash(error)
                    return render_template("auction.html", current_user = username)

                # set a limit to item price, item price must between 1 to 100 characters
                if (len(get_item_price) >= 1 and len(get_item_price) <= 100):
                    # Make sure price input only contains numbers
                    # If all characters in item price are numbers
                    if (get_item_price.isnumeric() == True):
                        # set ".00" to the end of the price
                        get_item_price = get_item_price + ".00"
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
                                    error = "Invalid item price, Please make sure set the price to two decimal places"
                                    flash(error)
                                    return render_template("auction.html", current_user = username)

                            if (len(price_after_dot) == 2):
                                if (price_after_dot.isnumeric() == True):
                                    pass
                                else:
                                    error = "Invalid item price, Please make sure set the price to two decimal places"
                                    flash(error)
                                    return render_template("auction.html", current_user = username)
                            elif (len(price_after_dot) == 1):
                                if (price_after_dot.isnumeric() == True):
                                    get_item_price = get_item_price + '0'
                                else:
                                    error = "Invalid item price, Please make sure set the price to two decimal places"
                                    flash(error)
                                    return render_template("auction.html", current_user = username)
                            else:
                                error = "Invalid item price, make sure set the price to two decimal places"
                                flash(error)
                                return render_template("auction.html", current_user = username)
                        else:
                            error = "Invalid item price"
                            flash(error)
                            return render_template("auction.html", current_user = username)
                else:
                    error = "Invalid item price"
                    flash(error)
                    return render_template("auction.html", current_user = username)

                # set a limit to item image, number of item images must be 1
                if (get_item_image.filename != ''):
                    image_split_list = get_item_image.filename.split(".")
                    if (image_split_list[1] in ALLOWED_EXTENSIONS):
                        filename = secure_filename(get_item_image.filename)
                        get_item_image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                    else:
                        error = "Invalid Item Image, Make sure the type of the file is jpg or jpeg"
                        flash(error)
                        return render_template("auction.html", current_user = username)
                else:
                    error = "Invalid Item Image, Make sure upload an image"
                    flash(error)
                    return render_template("auction.html", current_user = username)

            # <-- All inputs are valid at this point -->
            # build current auction informations
            auction_content = {}
            auction_content["posted_user"] = username
            auction_content["auction_id"] = get_next_id()
            auction_content["item_name"] = get_item_name
            auction_content["item_description"] = get_item_description
            auction_content["item_image"] = filename
            auction_content["auction_current_price"] = get_item_price
            auction_content["highest_bid_user"] = username
            auction_content["auction_end_time"] = get_end_time
            # Store all inputs into the auction database
            auction_collection.insert_one(auction_content)
            print("auction_collection: " + str(list(auction_collection.find({}, {"_id": 0}))), flush=True)

            # Store all inputs into current user's database
            get_user_from_database = list(users_collection.find({"username": username}, {"_id": 0}))
            # get current user's "auctions" list
            user_auction_list = get_user_from_database[0]["auctions"]
            user_auction_list.append(auction_content)
            users_collection.update_one({'username': username}, {"$set": {"auctions" : user_auction_list}})
            print("user_collection: " + str(list(users_collection.find({}, {"_id": 0}))), flush=True)

            return redirect(url_for("signed_in"))



@socketio.on('message')
def handle_message(data):
    print('received_data (message): ' + data, flush=True)
    send(data)


@socketio.on('auction')
def handle_auction(dict):
    print('received_dict: ' + str(dict), flush=True)
    print('received_id: ' + str(dict["id"]), flush=True)
    print('received_bid: ' + str(dict["price"]), flush=True)

    error = ''
    get_item_price = dict["price"]
    #print("current_bid" + get_item_price, flush=True)

    # check if the entered price is valid or not
    if (len(get_item_price) >= 1 and len(get_item_price) <= 100):
        # Make sure price input only contains numbers
        # If all characters in item price are numbers
        if (get_item_price.isnumeric() == True):
            # set ".00" to the end of the price
            get_item_price = get_item_price + ".00"
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
                        error = "Invalid item price, Please make sure set the price to two decimal places"
                        flash(error)
                if (len(price_after_dot) == 2):
                    if (price_after_dot.isnumeric() == True):
                        pass
                    else:
                        error = "Invalid item price, Please make sure set the price to two decimal places"
                        flash(error)
                elif (len(price_after_dot) == 1):
                    if (price_after_dot.isnumeric() == True):
                        get_item_price = get_item_price + '0'
                    else:
                        error = "Invalid item price, Please make sure set the price to two decimal places"
                        flash(error)
                else:
                    error = "Invalid item price, make sure set the price to two decimal places"
                    flash(error)
            else:
                error = "Invalid item price"
                flash(error)
    else:
        error = "Invalid item price"
        flash(error)

    if (error == ''):
        print("current_bid: " + get_item_price, flush=True)
        # check is the new bid higher than the old bid
        auction_current_price = list(auction_collection.find({"auction_id": int(dict['id'])}, {"_id": 0}))[0]['auction_current_price']
        if (float(get_item_price) > float(auction_current_price)):
            if ('auth_token' in session):
                # get auth_token in session
                get_auth_token = session['auth_token']
                print("Current_auth_token: " + get_auth_token, flush=True)
                # user auth_token get the username
                # hash the auth token that we got from the request
                sha256_auth_token = hashlib.sha256()
                sha256_auth_token.update(get_auth_token.encode())
                hashed_auth_token = sha256_auth_token.digest()
                # check if the hashed auth token exist in our database
                check_exist = list(users_collection.find({"auth_token": hashed_auth_token}, {"_id": 0}))
                if (len(check_exist) == 0):
                    pass
                else:
                    print("Current_username: " + check_exist[0]["username"], flush=True)
                    # update the auction's "auction_current_price" and "highest_bid_user" in auction database
                    auction_collection.update_one({'auction_id': int(dict["id"])}, {"$set": {"auction_current_price" : get_item_price}})
                    auction_collection.update_one({'auction_id': int(dict["id"])}, {"$set": {"highest_bid_user" : check_exist[0]["username"]}})

                    # update the auction in posted user's auction list
                    current_auction = list(auction_collection.find({"auction_id": int(dict["id"])}, {"_id": 0}))[0]
                    # get the "posted username"
                    posted_username = current_auction['posted_user']
                    # get the auction list for the "posted_user"
                    posted_user_auction_list = list(users_collection.find({"username": posted_username}, {"_id": 0}))[0]['auctions']
                    # update "posted_user_auction_list"
                    for auction in posted_user_auction_list:
                        if (auction['auction_id'] == int(dict["id"])):
                            auction["auction_current_price"] = get_item_price
                            auction["highest_bid_user"] = check_exist[0]["username"]
                        else:
                            pass
                    # update "posted_user_auction_list" in user's database
                    users_collection.update_one({'username': posted_username}, {"$set": {"auctions" : posted_user_auction_list}})

                    # change dict["price"] to get_item_price
                    dict["price"] = get_item_price
                    emit('auction', dict, broadcast=True)
            else:
                pass
        else:
            pass
    else:
        pass


@socketio.on('count_down')
def handle_count_down(dict):

    print('received_id: ' + str(dict['auction_id']), flush=True)
    print('received_time: ' + str(dict['count_down']), flush=True)
    if (str(dict['count_down']) != '0'):
        # update "auction_end_time" in auction collection
        auction_collection.update_one({'auction_id': int(dict['auction_id'])}, {"$set": {"auction_end_time" : str(dict['count_down'])}})
        #emit('countdown', dict, broadcast=True)
    else:
        # update "auction_end_time" in auction collection
        auction_collection.update_one({'auction_id': int(dict['auction_id'])}, {"$set": {"auction_end_time" : 'Expired'}})
        emit('countdown', {"auction_id": dict['auction_id'], "count_down": 'Expired'}, broadcast=True)
        




if __name__ == '__main__':
    socketio.run(app, host = "0.0.0.0", port = 8080, debug = True)
    #app.run(host = "0.0.0.0", port = 8080, debug = True)






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
