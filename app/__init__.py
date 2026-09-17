from app.db import Users, BackgroundsList, GlobalSettings
from flask import Flask, render_template, jsonify, request, session, redirect, url_for, send_file
from werkzeug.security import generate_password_hash, check_password_hash
import base64
import json
import uuid
import io

app = Flask("FLEPcyber")
app.config["SECRET_KEY"] = str(uuid.uuid4())

app.config['SESSION_COOKIE_SECURE'] = False    # HTTP blocker
app.config['SESSION_COOKIE_HTTPONLY'] = True   # HTTP only

app.config.update(SESSION_COOKIE_SECURE=False, SESSION_COOKIE_SAMESITE="Lax")

users_num = Users.select().count()
if not users_num:
    Users(
        uid=str(uuid.uuid4()),
        username="admin",
        password=None,
        createPasswordMode=1,
        email=None,
        classLevel=3
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if "userId" in session:
        if request.method == "GET":
            images = BackgroundsList.select()
            selected = GlobalSettings.select()
            if selected.count():
                selected = selected[0]
            else:
                GlobalSettings(selectedImage = -1)
                selected = selected[0]
            selected = selected.selectedImage
            return render_template("panel.html", images=images, selected=selected)
        if request.method == "POST":
            if 'image' not in request.files:
                return "Aucun fichier envoyé", 400
            file = request.files['image']
            if file.filename == '':
                return "Aucun fichier sélectionné", 400
            if file:
                image_bytes = file.read()
                base64_string = base64.b64encode(image_bytes).decode('utf-8')
                mime_type = file.content_type
                data_url = f"data:{mime_type};base64,{base64_string}"
                check_data = BackgroundsList.selectBy(image = data_url)
                message = None
                if not check_data.count():
                    BackgroundsList(image=data_url)
                    message = "Validé"
                images = BackgroundsList.select()
                selected = GlobalSettings.select()
                if selected.count():
                    selected = selected[0]
                else:
                    GlobalSettings(selectedImage = -1)
                    selected = selected[0]
                selected = selected.selectedImage
                return render_template("panel.html", message=message, images=images, selected=selected)
    return redirect(url_for('login'))

@app.route("/bg", methods=["GET"])
def bg_red():
    return redirect(url_for("bg"))
@app.route("/bg/", methods=["GET"])
def bg():
    global_settings = GlobalSettings.select()
    if global_settings.count():
        if global_settings[0].selectedImage > -1:
            data_url = BackgroundsList.get(global_settings[0].selectedImage).image
            header, data_base64 = data_url.split(',', 1)
            mime_type = header.split(';')[0].split(':')[1]
            image_bytes = base64.b64decode(data_base64)
            buffer = io.BytesIO(image_bytes)
            return send_file(buffer, mimetype=mime_type)
        else:
            return "Not found", 404
    GlobalSettings(selectedImage = -1)
    return redirect(url_for("bg"))

@app.route("/bg/<id>/", methods=["GET"])
def bg_select(id):
    image = BackgroundsList.selectBy(id = id)
    if image.count():
        global_settings = GlobalSettings.select()
        if global_settings.count():
            global_settings[0].selectedImage = int(id)
            return redirect(url_for("index"))
        else:
            GlobalSettings(selectedImage = -1)
            return redirect()
    else:
        return "Not Found"

@app.route("/logout/", methods=["GET", "POST"])
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/login/", methods=["GET", "POST"])
def login():
    if "userId" in session:
        return redirect(url_for("index"))
    if request.method == "GET":
        session.clear()
        return render_template("login.html", step = 1)
    elif request.method == "POST":
        username = str(request.form["username"])
        if not username and not session.get("username"):
            return redirect("login")
        password = request.form.get("password")
        if not password or not password.strip():
            password = None
        account = Users.selectBy(username = username)
        if not password:
            if account.count() == 1 and account[0].createPasswordMode == 1:
                session["userId"] = account[0].uid
                session.modified = True
                return redirect(url_for('create_password'))
            return render_template("login.html", step = 2, username = username)
        else:
            hash_stored = account[0].password
            if check_password_hash(hash_stored, password):
                session["userId"] = account[0].uid
                session.modified = True
                return redirect(url_for("index"))
            else:
                session.clear()
                return render_template("login.html", step = 4, error = "Identifiant ou mot de passe incorrect")
    return "500 Internal Server Error", 500

@app.route("/create_password/", methods=["GET", "POST"])
def create_password():
    user_id = session.get("userId")
    print(user_id)
    if not user_id:
        return redirect(url_for('index'))
    if request.method == "GET":
        user = Users.selectBy(uid=user_id)
        if user.count() == 1:
            username = user[0].username
            return render_template("login.html", step = 3, username = username)
        session.clear()
        return redirect(url_for("index"))
    if request.method == "POST":
        user = Users.selectBy(uid=user_id)
        if user.count() == 1:
            user = user[0]
        else:
            return "ERROR"
        password = request.form.get("password")
        hash_pass = generate_password_hash(password)
        user.password = hash_pass
        user.createPasswordMode = 0
        return redirect(url_for("index"))
    return "500 Internal Server Error", 500

@app.route("/settings/", methods=["GET", "POST"])
def settings():
    return "ERROR 500"
    

@app.after_request
def add_header(response):
    response.headers["Access-Control-Allow-Origin"] = request.headers.get("Origin")
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = (
        "Content-Type, Authorization, TOKEN, token"
    )
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    return response


app.run(port=8000, host="0.0.0.0", threaded=True, debug=True)
