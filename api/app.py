#coding: utf-8

import json
import urllib.parse
import string
import random
import os
import socket
import hashlib
import redis
from flask import Flask, Response, jsonify, request
from urllib.parse import urlparse, urlencode, quote_plus

red = redis.Redis(host="redis-server", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)

# @app.route("/md5/<string:words>")
# def md5(words, chars=string.ascii_letters + string.digits):
#     x="{"
#     y="}"
#     leng = len(words)
#     words = urllib.parse.quote(words)
#     txt=(''.join(random.choice(chars) for x in range(leng)))
#     return f"{x}\n\"input\": {words},\n\"output\": {txt}\n{y}"

@app.route('/md5/<string:words>')
def md5(words):
    return jsonify(
        input=words,
        output=hashlib.md5(words.encode('utf8')).hexdigest()
    )

@app.route("/factorial/<int:num>")
def factor(num,fact=1):
    x="{"
    y="}"
    for i in range(1,num+1):
        fact = fact * i
    return f"{x}\n\"input\": {num},\n\" output\": {fact}\n{y}"

@app.route('/fibonacci/<int:val>')
def term(val):
    x="{"
    y="}"
    Out = 0
    Sequence = [0,1]
    if val > 0:
        while Out < val:
            Out = Sequence[-1] + Sequence[-2]
            if (Out < val):
                Sequence.append(Out)
        return f"{x}\n\"input\": {val},\n\"output\": {Sequence}\n{y}"
    elif val <=0:
        return f"That is not a valid number"

@app.route("/is-prime/<int:num>")
def prime(num):
    x="{"
    y="}"
    a = "True"
    b = "False"
    if num > 1:
        for i in range(2, int(num/2)+1):
            if (num % i) == 0:
                return f"{x}\n\"input\": {num},\n\"output\": {b}\n{y}"
        else:
            return f"{x}\n\"input\": {num},\n\"output\": {a}\n{y}"
    else:
        return f"{x}\n\"input\": {num},\n\"output\": {b}\n{y}"
    return

@app.route('/slack-alert/<string:text>')
def alert(text):
    from urllib import request, parse
    x="{"
    y="}"
    a = "True"
    b = "False"
    post = {"text": "{0}".format(text)}
    try:
        json_data = json.dumps(post)
        req = request.Request("https://hooks.slack.com/services/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",data=json_data.encode('ascii'),headers={'Content-Type': 'application/json'}) 
        resp = request.urlopen(req)
        return f"{x}\n\"input\": {text},\n\"output\": {a}\n{y}"     
    except Exception as em:
        print("EXCEPTION: " + str(em))
        return f"{x}\n\"input\": {text},\n\"output\": {b}\n{y}"
    alert(f'{text}')
    
@app.route('/keyval', methods=['POST', 'PUT'])
def kv_upsert():
    _JSON = {
        'key': None,
        'value': None,
        'command': 'CREATE' if request.method=='POST' else 'UPDATE',
        'result': False,
        'error': None
    }

    try:
        payload = request.get_json()
        _JSON['key'] = payload['key']
        _JSON['value'] = payload['value']
        _JSON['command'] += f" {payload['key']}/{payload['value']}"
    except:
        _JSON['error'] = "Missing or malformed JSON in client request."
        return jsonify(_JSON), 400

    try:
        test_value = redis.get(_JSON['key'])
    except redis.RedisError:
        _JSON['error'] = "Cannot connect to redis."
        return jsonify(_JSON), 400
    
    if request.method == 'POST' and not test_value == None:
        _JSON['error'] = "Cannot create new record: key already exists."
        return jsonify(_JSON), 409 
    if request.method == 'PUT' and test_value == None:
        _JSON['error'] = "Cannot update record: key does not exist."
        return jsonify(_JSON), 404

    else:
        if redis.set(_JSON['key'], _JSON['value']) == False:
            _JSON['error'] = "There was a problem creating the value in Redis."
            return jsonify(_JSON), 400
        else:
            _JSON['result'] = True
            return jsonify(_JSON), 200

@app.route('/keyval/<string:k>', methods=['GET','DELETE'])
def gdkey(k):
    JSON = {
        "key": k,
        "value": None,
        "command": "{} {}".format('RETRIEVE' if request.method=='GET' else 'DELETE', k),
        "result": False,
        "error": None
    } 
    try:
        test = redis.get(k)
    except redis.RedisError:
        JSON['error'] = "Cannot connect to redis."
        return jsonify(JSON), 400
    if test == None:
        JSON['error'] = "Key does not exist"
        return jsonify(JSON), 404
    else:
        JSON['value'] = test.decode('unicode-escape')

    if request.method == 'GET':
        JSON['result'] = True
        return jsonify(JSON), 200
    elif request.method == 'DELETE':
        JSON['result'] = True
        return jsonify(JSON), 200
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
