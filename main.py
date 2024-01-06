import os

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# json soonTM
challenges = {}
users = {}

class User:
    def __init__(self, username, pwd):
        self.username = username
        self.password = pwd
        self.score = 0
        self.c_points={}
        for challenge in challenges:
            self.c_points[challenge]=0

    def add_score(self, challenge, n):
        self.c_points[challenge]=n
        self.score += n

class Challenge:
    def __init__(self, cname, desc, answer):
        self.cname = cname
        self.desc = desc
        self.answer = answer

@app.route('/admin/submit_challenge', methods=['POST'])
def submit_challenge():
    auth = request.json['auth']
    if auth != "53CUR3_P455W0RD": # lol
        return {"status": False}

    cname = request.json['cname']
    desc = request.json['desc']
    answer = request.json['answer']
    
    challenges[cname] = Challenge(cname, desc, answer)
    return {"status": True}, 201
    
@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    pwd = request.json['password']
    if username in users:
        return {"status": False}
    
    users[username] = User(username, pwd)
    return {"status": True}, 201


@app.route('/submit', methods=['POST']) # sus
def validate():
    cname = request.json['cname'] # challenge name/id
    submitted_ans = request.json['submit'].lower # submitted answer from user
    username = request.json['username']
    points=request.json['points']
    if submitted_ans == challenges[cname].answer:
        users[username].add_score(points) # add a point
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
    return render_template('admin.html', users = users, challenges = challenges)

@app.route('/', methods=['GET'])
def homepage():
    return {"status": True}, 201

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5001')
