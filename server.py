import os
import subprocess

from flask import jsonify
from flask import request, redirect, render_template, url_for, session

from flask_jwt_extended import create_access_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager

from flask_login import LoginManager, login_user, login_required, current_user, login_manager


from model import app
from model import User

from util import JWT_secret
from util import check_password, append_new_line

# Setup the Flask-JWT-Extended extension
app.config["JWT_SECRET_KEY"] = JWT_secret
jwt = JWTManager(app)

PATH_TO_HOST_ALLOW = os.environ.get("PATH_TO_HOST_ALLOW", 'hosts.allow')
PATH_TO_HOSTS = os.environ.get("PATH_TO_HOSTS", 'hosts')
PATH_TO_NAS_FOLDER = os.environ.get("PATH_TO_NAS_FOLDER", '/nas')

app.secret_key = os.urandom(12)
login = LoginManager(app)
login.init_app(app)
login.login_view = "login"

@login.user_loader
def load_user(id):
    return User.query.get(int(id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    if request.method == 'GET':
        return render_template('login.html')
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user == None:
            # flash('wrong password!')
            return index()
        if password == user.password:
            login_user(user)
            return redirect('/')

@app.route("/logout")
def logout():
    session['admin'] = False
    return redirect('/')

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    try:
        user = User.query.get(current_user.get_id())
        return render_template('index.html')
    except:
        return render_template('login.html')


@app.route("/api/login", methods=["POST"])
def login_api():
    username = request.json.get('username')
    password = request.json.get('password')
    if not username or not password:
        return jsonify({"msg": "Missing username or password"}), 401

    user = User.query.filter_by(username=username).first()
    if user is None:
        return jsonify({"msg": "User not found"}), 401
    if not check_password(password, user.password):
        return jsonify({"msg": "Password is incorrect"}), 401
    # return user
    # return dict(user_id=user.id)
    access_token = create_access_token(identity=username)
    return jsonify(access_token=access_token)

@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    # Access the identity of the current user with get_jwt_identity
    current_user = get_jwt_identity()
    return jsonify(logged_in_as=current_user), 200

@app.route("/api/registry", methods=["POST"])
# @jwt_required()
def registry_hosts():
    # Access the identity of the current user with get_jwt_identity
    # current_user = get_jwt_identity()
    camID = request.json.get('id')
    IP = request.json.get('ip')
    accessKey = request.json.get('key')
    if accessKey != 'aivis2022nfs':
        return jsonify({"msg": "wrong access key"}), 401

    # check camid exist in hosts.allow
    with open(PATH_TO_HOSTS) as f:
        if camID in f.read():
            print("camID exist")
            #Delete line part
            cmd = "sed -i s/.*{}.*// {}".format(camID, PATH_TO_HOSTS)
            print(cmd)
            subprocess.run(cmd.split(' '))

    # Append new lines at the end
    newClientLine = "{} {}.aivis.tech".format(IP, camID)
    append_new_line(PATH_TO_HOSTS, newClientLine)

    # Set folder /nas accessible all
    cmd1 = "sudo chown -R nobody:nogroup {}".format(PATH_TO_NAS_FOLDER)
    cmd2 = "sudo chmod -R 777 {}".format(PATH_TO_NAS_FOLDER)
    print(cmd1)
    print(cmd2)
    subprocess.run(cmd1.split(' '))
    subprocess.run(cmd2.split(' '))

    return jsonify({"msg": "success"}), 200


def registry_hots_allow():
    # Access the identity of the current user with get_jwt_identity
    # current_user = get_jwt_identity()
    camID = request.json.get('id')
    IP = request.json.get('ip')
    accessKey = request.json.get('key')
    if accessKey != 'aivis2022nfs':
        return jsonify({"msg": "wrong access key"}), 401

    # check camid exist in hosts.allow
    with open(PATH_TO_HOST_ALLOW) as f:
        if '#{}'.format(camID) in f.read():
            print("camID exist")
            #Delete line part
            cmd1 = "sed -z s/#{}\\n/#{}/ -i {}".format(camID, camID, PATH_TO_HOST_ALLOW)
            cmd2 = "sed -i s/#{}.*// {}".format(camID, PATH_TO_HOST_ALLOW)
            print(cmd1.split(' '))
            print(cmd2)
            subprocess.run(cmd1.split(' '))
            subprocess.run(cmd2.split(' '))

    # Append new lines at the end
    newClientLine1 = "#{}".format(camID)
    newClientLine2 = "ALL : {} : allow".format(IP)
    append_new_line(PATH_TO_HOST_ALLOW, newClientLine1)
    append_new_line(PATH_TO_HOST_ALLOW, newClientLine2)
    return jsonify({"msg": "success"}), 200

if __name__ == "__main__":
    port = os.environ.get("PORT", 8080)
    if port == 8080:
        app.run('0.0.0.0', port=port)
    else:
        app.run('0.0.0.0', port=port, ssl_context=('cert/extensions.aivis.tech/server_certificate.pem', 'cert/extensions.aivis.tech/server_key.pem'))