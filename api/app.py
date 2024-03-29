#coding: utf-8

import json
import urllib.parse
import string
import random
import os
import socket
import hashlib
import redis
import requests
from flask import Flask, Response, jsonify, request
from urllib.parse import urlparse, urlencode, quote_plus
from math import sqrt

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

def fib(n):
    f_1, f_2 = 0, 1
    ret = [0]
    while f_2 <= n:
        ret.append(f_2)
        f_1, f_2 = f_2, f_1 + f_2
    return ret

@app.route('/fibonacci/<int:input_int>')
def fibonacchi_resp(input_int):
    return jsonify(
        input=input_int,
        output=fib(input_int)
    )

def is_prime(n):
    if n < 2: return False
    for x in range(2, int(sqrt(n)) + 1):
        if n % x == 0:
            return False
    return True

@app.route('/is-prime/<int:input_int>')
def prime_check(input_int):
    return jsonify(
        input=input_int,
        output=is_prime(input_int)
    )

@app.route('/slack-alert/<string:msg>')
def post_to_slack(msg):
    data = { 'text': msg }
    resp = requests.post("https://hooks.slack.com/services/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", json=data)
    if resp.status_code == 200:
        result = True
        mesg = "Message successfully posted to Slack channel "
    else:
        result = False
        mesg = "There was a problem posting to the Slack channel (HTTP response: " + str(resp.status_code) + ")."

    return jsonify(
        input=msg,
        message=mesg,
        output=result
    ), 200 if resp.status_code==200 else 400
    
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
