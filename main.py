import os

from flask import Flask, request, jsonify
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
    def __init__(self, cname, desc, answer, value):
        self.cname = cname
        self.desc = desc
        self.answer = answer
        self.value = value

def add_challenge(cname, desc, answer):
    challenges[cname] = Challenge(cname, desc, answer)

@app.route('/register', methods=['POST'])
def register(username, pwd):
    if username in users:
        return False
    
    users[username] = User(username, pwd)
    return True


@app.route('/submit', methods=['POST']) # not working
def validate():
    cname = request.json['cname'] # challenge name/id
    submitted_ans = request.json['submit'].lower # submitted answer from user
    username = request.json['username']

    if submitted_ans == challenges[cname].answer:
        users[username].add_score(challenges[cname].value)
        return True
    return False
        


if __name__ == '__main__':
    app.run(debug=True)