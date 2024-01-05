import os

from flask import Flask, request, jsonify
app = Flask(__name__)

# make key dict like this (from json?)
key = {'challenge id': 'answer'}

@app.route('/api/submit', methods=['POST'])
def validate():
    id = request.json['challenge'] # challenge name/id
    submit = request.json['submit'] # submitted answer from user

    submit = submit.lower

    return submit == key[id]

if __name__ == '__main__':
    app.run(debug=True)