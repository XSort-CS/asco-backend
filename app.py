import os
import json
import time

from flask import Flask, render_template, request, jsonify
from flask_cors import CORS

users = {}
challenges = {}

AUTH = "x"
app = Flask(__name__)
CORS(app)

# @app.before_first_request depricated. fix tmr.
def loadData():
    global users
    global challenges
    print("[!] Loading data...")
    with open('challenges.json', 'r') as f:
        challenges = json.load(f)
    with open('users.json', 'r') as f:
        users = json.load(f)

    for cname in challenges.keys():
        challenge_dict = challenges[cname]
        challenges[cname] = Challenge(challenge_dict['cname'], challenge_dict['desc'], challenge_dict['answer'])
    for user in users.keys():
        user_dict = users[user]
        users[user] = User(user_dict['username'], user_dict['password'])

def saveData():
    print("[!] Saving data...")
    c_save = {}
    u_save = {}
    for key in challenges.keys():
        c_save[key] = challenges[key].toJson()
    for key in users.keys():
        u_save[key] = users[key].toJson()

    with open('challenges.json', 'w') as f:
        json.dump(c_save, f)
    with open('users.json', 'w') as f:
        json.dump(u_save, f)

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

    def toJson(self):
        out = {}
        out["username"] = self.username
        out["password"] = self.password
        out["score"] = self.score
        out["c_points"] = self.c_points
        return out

class Challenge:
    def __init__(self, cname, desc, answer):
        self.cname = cname
        self.desc = desc
        self.answer = answer

    def toJson(self):
        out = {}
        out["cname"] = self.cname
        out["desc"] = self.desc
        out["answer"] = self.answer
        return out


@app.route('/admin/submit_challenge', methods=['POST'])
def submit_challenge():
    auth = request.json['auth']
    if auth != AUTH: # lol
        return {"status": False}

    cname = request.json['cname']
    desc = request.json['desc']
    answer = request.json['answer']
    
    challenges[cname] = Challenge(cname.strip(), desc.strip(), answer.strip())
    saveData()
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
    saveData()
    return {"status": True, "message": "Updated user cpoints dict"}

@app.route('/admin/del_user', methods=['POST'])
def del_user():
    auth = request.json.get('auth')
    if auth != AUTH:
        return {"status": False, "message": "Authentication failed."}
    
    user = request.json.get('username')
    value = users.pop(user)
    saveData()
    return {"message": value}

@app.route('/register', methods=['POST'])
def register():
    username = request.json['username']
    pwd = request.json['password']
    if username in users:
        return {"status": False, "message": "Username taken."}
    
    users[username] = User(username, pwd)
    update_users()
    saveData()
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
    saveData()
    return {"status": False}

@app.route('/dragon', methods=['POST']) # sus
def dragon():
    cname = "dragon"
    username = request.json['username']
    submitted_ans = request.json['submit'].lower()
    points=request.json['points']
    value=process_dragon(submitted_ans)
    if(value=='Dragon Defeated!!'):
       users[username].add_score(cname, points) # submitted answer from user
    saveData()
    return {"value": value}

@app.route('/completion', methods=['POST']) # sus
def completion():
    cname = request.json['cname'] # challenge name/id
   # submitted answer from user
    username = request.json['username']
    saveData()
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

#Challenge-Specific Functions
def process_dragon(program):
  if(len(program)==0):
    return "You died of nothingness"
  d_health=1000;
  cur_index=0;
  loops_left=-1
  loop_start=0;
  i=0;
  while(i<2001):
    i+=1
    if(cur_index>=len(program)):
      if(loops_left>0):
        return "You died of an unclosed {"
      cur_index=0;
    if(program[cur_index]=="}"):
      if(loops_left==-1):
        return "You died of an unclosed }"
      if(loops_left>0):
        cur_index=loop_start
        loops_left-=1;
        i-=1;
        continue;
      else:
        cur_index=cur_index+1
        loops_left=-1
        i-=1;
        continue;
    if(program[cur_index]=='x'):
        d_health-=1;
        if(d_health<=0):
          return "Dragon Defeated!!"
    if(program[cur_index]!='s' and (i%200)%3==2 and (i%200)!=2):
        return "You died on round {}".format(i)
    if(program[cur_index]=="{"):
      if(loops_left>0):
        return "You died of a nested loop"
      else:
        if(cur_index+1>=len(program)):
          return "You died of a bad loop"
        I=cur_index+2
        num=0
        while(program[cur_index+1:I].isnumeric()):
          if(I>=len(program)):
            return "You died of a bad loop"
          num=int(program[cur_index+1:I])
          I+=1;
        if(I==cur_index+2):
          return "You died of a bad loop"
        cur_index=I-1
        loop_start=cur_index
        loops_left=num-1
        i-=1;
        continue;
    cur_index+=1;
  return "You died of old age."

if __name__ == '__main__':
    loadData()
    app.run(host='0.0.0.0', port='5001')