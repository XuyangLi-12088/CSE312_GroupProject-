from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/sign_up", methods=["GET", "POST"])
def sign_up():
    #if (request.method == "POST"):

    print(request.method)
    print(request.path)
    print(request.form)
    print(request.form["username"])
    print(request.form["password"])
    return render_template("sign_up.html")

@app.route("/login", methods=["GET", "POST"])
def login():

    print(request.method)
    print(request.path)
    print(request.form)
    print(request.form["username"])
    print(request.form["password"])
    return render_template("login.html")

@app.route("/post", methods=["GET", "POST"])
def post():
    #if (request.method == "POST"):

    print(request.method)
    print(request.path)
    print(request.form)
    print(request.form["item_name"])
    print(request.form["item_description"])
    print(request.files["item_images"])
    print(request.form["item_price"])
    return render_template("post.html")
