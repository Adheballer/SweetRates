from flask import Flask, render_template, request, redirect, url_for, flash, session
import uuid
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
import os
import json

UPLOAD_FOLDER = 'user_uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}
USERS_FILE = "carusers.json"

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "fallback-secret")
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def load_users():
    """Load users from JSON file, return list"""
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return []
    return []


def save_users(users):
    """Save users list to JSON file"""
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    myid = uuid.uuid1()
    if request.method == "POST":
        rec_id = request.form.get("uuid")
        desc = request.form.get("text")
        input_files = []

        
        folder_path = os.path.join(app.config['UPLOAD_FOLDER'], rec_id)
        os.makedirs(folder_path, exist_ok=True)

        for key, file in request.files.items():
            if file:
                filename = secure_filename(file.filename)
                file.save(os.path.join(folder_path, filename))
                input_files.append(filename)

        with open(os.path.join(folder_path, "desc.txt"), "w") as f:
            f.write(desc)
        input_txt = os.path.join(folder_path, "input.txt")
        with open(input_txt, "w") as f:
            for fl in input_files:
                f.write(f"file '{fl}'\n")
                f.write("duration 2\n")
            if input_files:
                f.write(f"file '{input_files[-1]}'\n")

    return render_template("create.html", myid=myid)

@app.route("/gallery")
def gallery():
    reels = [f for f in os.listdir("static/reels") if f.endswith(".mp4")]
    return render_template("gallery.html", reels=reels)

@app.route("/login", methods=["GET", "POST"])
def login():
    email_error = None
    password_error = None

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        users = load_users() 

        user = next((u for u in users if u["email"] == email), None)

        if not email:
            email_error = "Email is required"
        elif not user:
            email_error = "Email not registered"

        if not password:
            password_error = "Password is required"
        elif user and not check_password_hash(user["password"], password):
            password_error = "Incorrect password"

        if not email_error and not password_error:
            session['user'] = user["fullname"]
            flash("Login successful!", "success")
            return redirect(url_for("index"))

    return render_template("login.html", email_error=email_error, password_error=password_error)


@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        fullname = request.form['fullname']
        email = request.form['email']
        password = request.form['password']
        confirm = request.form['confirm']

        if password != confirm:
            flash("Passwords do not match!", "danger")
            return render_template("signup.html")

        users = load_users()

        if any(user['email'] == email for user in users):
            flash("Email already registered!", "warning")
            return render_template("signup.html")

        hashed_password = generate_password_hash(password)

        new_user = {
            "fullname": fullname,
            "email": email,
            "password": hashed_password
        }
        users.append(new_user)
        save_users(users)

        flash("Signup successful! You can now log in.", "success")
        return redirect(url_for("login"))

    return render_template("signup.html")

if __name__ == "__main__":
    app.run(debug=True)
