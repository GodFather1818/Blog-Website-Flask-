from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, abort
# from flask_pymongo import PyMongo
from pymongo import MongoClient
import os
from bson import ObjectId
import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, EqualTo
from werkzeug.security import generate_password_hash, check_password_hash
from flask import flash


load_dotenv()
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY')  

client = MongoClient(os.environ.get('CONNECT'))
db = client.pythonblogsDB  # Replace 'pythonblogsDB' with your actual database name
mongo = db.blog
mongo_user = db.userData

year  = datetime.date.today().year


# MongoDB schema definition
blog_schema = {
    "postTitle": {"type": str},
    "content": {"type": str},
    "date": {"type": datetime},
    "username": {"type": str},
    "password": {"type": str}
}

user_schema = {
    "useraname": {"type": str},
    "password": {"type": str}

}


class RegistrationForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo("password")])
    submit = SubmitField("Sign Up")

# Define a simple form for user login
class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Log In")



@app.route("/signup", methods=["GET", "POST"])
def signup():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = mongo_user.find_one({"username": form.username.data})
        if existing_user:
            flash("Username already exists. Choose a different one.", "danger")
        else:
            hashed_password = generate_password_hash(form.password.data, method="scrypt")
            new_user = {"username": form.username.data, 
                        "password": hashed_password}
            mongo_user.insert_one(new_user)
            print(new_user)
            flash("Account created successfully! You can now log in.", "success")
            return redirect(url_for("login"))
    return render_template("signup.html", form=form)

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = mongo_user.find_one({"username": form.username.data})
        print(user)
        if user and check_password_hash(user["password"], form.password.data):
            session["user_id"] = str(user["_id"])
            session["username"] = str(user["username"])
             # Set a cookie for remembering the user
            # username = session.get("username")
            # print(username)
            print(f"User_Id: {session['user_id']}, username: {session['username']}")
            response = redirect(url_for("posts"))
            response.set_cookie("user_id", str(user["_id"]))
            flash("Logged in successfully!", "success")
            return response
            print(user)
        else:
            flash("Invalid username or password. Please try again.", "danger")
    return render_template("login.html", form=form)


@app.route("/")
def home():
    print(session)
    homeStartingContent = ''' 
                Lacus vel facilisis volutpat est velit egestas dui id ornare. 
                Semper auctor neque vitae tempus quam. Sit amet cursus sit amet 
                dictum sit amet justo. Viverra tellus in hac habitasse. Imperdiet
                proin fermentum leo vel orci porta. Donec ultrices tincidunt arcu
                 non sodales neque sodales ut. Mattis molestie a iaculis at erat pellentesque
    '''
    return render_template("home.html", homeContent=homeStartingContent, current_year=year)


@app.route("/about")
def about():
    aboutContent = ''' 
                Lacus vel facilisis volutpat est velit egestas dui id ornare. 
                Semper auctor neque vitae tempus quam. Sit amet cursus sit amet 
                dictum sit amet justo. Viverra tellus in hac habitasse. Imperdiet
                proin fermentum leo vel orci porta. Donec ultrices tincidunt arcu
                 non sodales neque sodales ut. Mattis molestie a iaculis at erat pellentesque
    '''
    return render_template("about.html", aboutContent=aboutContent, current_year=year)


@app.route("/contact")
def contact():
    contactContent = ''' 
                Lacus vel facilisis volutpat est velit egestas dui id ornare. 
                Semper auctor neque vitae tempus quam. Sit amet cursus sit amet 
                dictum sit amet justo. Viverra tellus in hac habitasse. Imperdiet
                proin fermentum leo vel orci porta. Donec ultrices tincidunt arcu
                 non sodales neque sodales ut. Mattis molestie a iaculis at erat pellentesque
    '''
    return render_template("contact.html", contactContent=contactContent, current_year=year)

@app.route("/compose")
def compose():
    if "user_id" in session:
        return render_template("compose.html")

    return redirect(url_for("login"))
    # return redirect(url_for("login"))


@app.route("/posts/<postId>")
def particular_post(postId):
    post = mongo.find_one({"_id": ObjectId(postId)})
    print(post)
    # return render_template("particularPost.html", newPosts=post)
    return render_template("particularPost.html", newPost=post, current_year=year)

@app.route("/posts")
def posts():
    # Check if the user is logged in
    if "user_id" not in session:
        abort(401)  # Unauthorized

    # Retrieve user information from the database
    user_id = session["user_id"]
    user = mongo_user.find_one({"_id": ObjectId(user_id)})

    # Check if the user exists in the database
    if not user:
        abort(401)  # Unauthorized

    # Now the user is authenticated. Proceeding Further
    posts = mongo.find({}).sort("date", -1)
    print(posts)
    return render_template("post.html", posts=posts, current_year=year, user=user)


@app.route("/", methods=["POST"])
def redirect_to_compose():
    if "user_id" in session:
        # User is logged in, redirect to the compose page
        return redirect(url_for("compose"))

    return redirect(url_for("login"))

@app.route("/compose", methods=["POST"])
def create_post():

    # user_id = session.get("user_id")
    # username = session.get("username")
    user_id = session['user_id']
    username = session['username']
    print(f"user_id: {user_id}\n username: {username}")
    user = mongo_user.find_one({"_id": ObjectId(user_id)})

    post = {
        "postTitle": request.form.get("postTitle"),
        "content": request.form.get("content"),
        "date":datetime.datetime.now(),
        "username": username,
        # "password": generate_password_hash(session.get("passowrd")),
        "user_id": user["_id"]
    }
    print(post)
    mongo.insert_one(post)
    print("Blog Insterted Successfully!")
    return redirect("/posts")


@app.route('/profile')
def profile():
    if "user_id" not in session:
        return redirect(url_for('login'))

    user_id = session["user_id"]
    user = mongo_user.find_one({"_id": ObjectId(user_id)})

    if not user:
        abort(401)  # Unauthorized

    user_posts = mongo.find({"user_id": user["_id"]}).sort("date", -1)
    
    return render_template('profile.html', user=user, user_posts=user_posts)




if __name__ == "__main__":
    app.run(debug=True)

