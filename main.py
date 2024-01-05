import os

from flask import Flask, render_template, request, jsonify
app = Flask(__name__)

# json soonTM
challenges = {}
users = {}

class User:
    def __init__(self, username, pwd):
        self.username = username
        self.password = pwd
        self.score = 0

    def add_score(n):
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
        return False

    cname = request.json['cname']
    desc = request.json['desc']
    answer = request.json['answer']
    
    challenges[cname] = Challenge(cname, desc, answer)
    return True

@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    pwd = request.json['password']
    if username in users:
        return False
    
    users[username] = User(username, pwd)
    return True


@app.route('/submit', methods=['POST']) # sus
def validate():
    cname = request.json['cname'] # challenge name/id
    submitted_ans = request.json['submit'].lower # submitted answer from user
    username = request.json['username']

    if submitted_ans == challenges[cname].answer:
        users[username].add_score(1) # add a point
        return True
    return False
        
@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    return render_template('admin.html', users = users, challenges = challenges)

@app.route('/', methods=['GET'])
def homepage():
    return f"hello world :)"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='5001')