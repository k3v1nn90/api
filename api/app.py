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

redis = redis.Redis(host="redis-server", db=0, socket_connect_timeout=2, socket_timeout=2)

app = Flask(__name__)

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
    return f"{x}\n\"input\": {num},\n\"output\": {fact}\n{y}"

@app.route('/fibonacci/<int:val>')
def term(val):
    x="{"
    y="}"
    f_1, f_2 = 0, 1
    val = [0]
    while f_2 <= n:
        val.append(f_2)
        f_1, f_2 = f_2, f_1 + f_2
        return f"{x}\n\"input\": {val},\n\"output\": {Sequence}\n{y}"
    elif val <=0:
        return f"That is not a valid number"

@app.route("/is-prime/<int:num>")
def prime(num):
    x="{"
    y="}"
    if num < 2: return False
    for x in range(2, int(sqrt(num)) + 1):
        if num % x == 0:
            return False
    return True

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
