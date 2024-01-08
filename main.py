import os
import json

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from flask_apscheduler import APScheduler

app = Flask(__name__)
scheduler = APScheduler()
CORS(app)
AUTH = "53CUR3_P455W0RD"

with open('challenges.json') as f:
    challenges = json.load(f)
with open('users.json') as f:
    users = json.loads(f)

def saveData():
    with open('challenges.json', 'w') as f:
        json.dumps(challenges, f)
    with open('users.json', 'w') as f:
        json.dumps(users, f)

class User:
    def __init__(self, username, pwd):
        self.username = username
        self.password = pwd
        self.score = 0
        self.c_points={}
        for challenge in challenges:
            self.c_points[challenge]=0

    def add_score(self, challenge, n):
        self.c_points[challenge] = n
        self.score += n

    def init_cpoints(self):
        for challenge in challenges:
            if not challenge in self.c_points.keys():
                self.c_points[challenge]=0

class Challenge:
    def __init__(self, cname, desc, answer):
        self.cname = cname
        self.desc = desc
        self.answer = answer

@app.route('/admin/submit_challenge', methods=['POST'])
def submit_challenge():
    auth = request.json['auth']
    if auth != AUTH: # lol
        return {"status": False}

    cname = request.json['cname']
    desc = request.json['desc']
    answer = request.json['answer']
    
    challenges[cname] = Challenge(cname.strip(), desc.strip(), answer.strip())
    return {"status": True}, 201
    
@app.route('/admin/delete_challenge', methods=['POST'])
def delete_challenge():
    auth = request.json.get('auth')
    
    if auth != AUTH:
        return {"status": False, "message": "Authentication failed."}

    cname_to_delete = request.json.get('cname')

    if cname_to_delete in challenges:
        del challenges[cname_to_delete]
        return {"status": True, "message": f"Challenge '{cname_to_delete}' deleted successfully."}
    else:
        return {"status": False, "message": f"Challenge '{cname_to_delete}' not found."}

@app.route('/admin/update_users', methods=['POST']) # fixes all users' cpoints data (run when adding a new challenge)
def update_users():
    auth = request.json.get('auth')

    if auth != AUTH:
        return {"status": False, "message": "Authentication failed."}

    for username in users:
        user = users[username]
        user.init_cpoints()
    
    return {"status": True, "message": "Updated user cpoints dict"}

@app.route('/admin/del_user', methods=['POST'])
def del_user():
    auth = request.json.get('auth')
    if auth != AUTH:
        return {"status": False, "message": "Authentication failed."}
    
    user = request.json.get('username')
    value = users.pop(user)
    return {"message": value}

@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    pwd = request.json['password']
    if username in users:
        return {"status": False, "message": "Username taken."}
    
    users[username] = User(username, pwd)
    update_users()
    return {"status": True, "message": f"User {username} registered successfully."}, 201


@app.route('/submit', methods=['POST']) # sus
def validate():
    cname = request.json['cname'] # challenge name/id
    submitted_ans = request.json['submit'].lower() # submitted answer from user
    username = request.json['username']
    points=request.json['points']
    if submitted_ans.strip() == challenges[cname].answer:
        users[username].add_score(cname, points) # add a point
        return {"status": True}
    return {"status": False}
    
@app.route('/completion', methods=['POST']) # sus
def completion():
    cname = request.json['cname'] # challenge name/id
   # submitted answer from user
    username = request.json['username']
    return {"status": users[username].c_points[cname]!=0}
        
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    cdisplay = []
    for cname in challenges.keys():
        challenge = challenges[cname]
        cdisplay.append( (challenge.cname, challenge.desc, challenge.answer) )

    udisplay = []
    for username in users:
        user = users[username]
        udisplay.append( (user.username, f"Total score: {user.score}", f"Data: {user.c_points}") )

    return render_template('admin.html', users = udisplay, cdisplay = cdisplay, password_required=True)

@app.route('/admin/login', methods=['POST'])
def admin_login():
    auth_password = AUTH
    password_attempt = request.json.get('password')

    # Check if the password is correct
    if password_attempt == auth_password:
        return {"status": True}
    else:
        return {"status": False}


@app.route('/', methods=['GET'])
def homepage():
    return {"status": True}, 201

if __name__ == '__main__':
    scheduler.add_job(func=saveData, trigger="interval", id="save_dicts_job", minutes=5)
    scheduler.start()
    app.run(host='0.0.0.0', port='5001', ssl_context='adhoc')
