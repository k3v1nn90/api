# -*- coding: utf-8 -*-

import requests
import hashlib
import os
import sys
import argparse
import subprocess

# Helper functions
def flatten(list):
    if len(list) > 1:
        return list
    else:
        return list[0]
    
encoding = 'utf-8'
    
# Grab the HOSTNAME and PORT to use for the HTTP connection from commandline arguments
parser = argparse.ArgumentParser(description='Test the TCMG 412 REST API.')
parser.add_argument('--host', dest='HOSTNAME', default='DOCKER_HOST', help='Specify the hostname')
parser.add_argument('--port', dest='PORT', default='5000', help='Specify the port')
args = parser.parse_args()

HOSTNAME = args.HOSTNAME
PORT = args.PORT

# Handle the special case of 'DOCKER_HOST'
if HOSTNAME == 'DOCKER_HOST':
    # group the docker host's IP address using the shell and `ip route`
    HOSTNAME = (subprocess.check_output(["/sbin/ip route | awk '/default/ { print $3 }'"], shell=True).strip())

# Check that the host and port are valid; exit with error if they are not
try:
    r = requests.get('http://' + str(HOSTNAME, encoding) + ':' + PORT + '/md5/test')
except (requests.exceptions.ConnectionError, requests.exceptions.Timeout, requests.exceptions.InvalidURL):
    print ("Unable to reach API at address: %s:%s...\n" % (HOSTNAME, PORT))
    print ("You can change the host or port using the --host and --port flags. Use -h for more info.\n")
    sys.exit(1)
else:
    print ("Testing REST API for on %s:%s...\n" % (HOSTNAME, PORT))


# Some constants for the API tests...
HASH_1 = '098f6bcd4621d373cade4e832627b4f6'   # 'test'
HASH_2 = '5eb63bbbe01eeed093cb22bb8f5acdc3'   # 'hello world'
FIB_SEQ = [0,1,1,2,3,5,8,13,21,34]
HTTP_ENCODE = "This%20is%20a%20longer%20string.%0D%0AIt%20even%20includes%20a%20newline..."

tests = [
    ('/md5/test',                 'GET',  [200], HASH_1),
    ('/md5/hello%20world',        'GET',  [200], HASH_2),
    ('/md5',                      'GET',  [400,404,405], None),
    ('/factorial/4',              'GET',  [200], 24),
    ('/factorial/check',           'GET',  [400,404,405], None),
    ('/factorial/0',              'GET',  [200], 1),
    ('/fibonacci/8',              'GET',  [200], FIB_SEQ[:7]),
    ('/fibonacci/35',             'GET',  [200], FIB_SEQ),
    ('/fibonacci/test',           'GET',  [400,404,405], None),
    ('/is-prime/1',               'GET',  [200], False),
    ('/is-prime/5',               'GET',  [200], True),
    ('/slack-alert/check',         'GET',  [200], True),
    ('/slack-alert/'+HTTP_ENCODE, 'GET',  [200], True),
    ('/kv-retrieve/test',        'GET',  [400,404,405], False),
    ('/kv-record/test',          'POST', [200], True, 'test1', 'fun'),
    ('/kv-retrieve/test',        'GET',  [200], 'fun'),
    ('/kv-record/test',          'POST', [400,404,405,409], False, 'test1', 'fun'),
    ('/kv-record/test1',          'POST', [200], True, 'test2', '34'),
    ('/kv-record/test',          'PUT',  [200], True, 'test1', 'thing'),
    ('/kv-retrieve/test',        'GET',  [200], 'thing'),
    ('/kv-record/test2',          'PUT',  [400,404,405,409], False, 'test3', '54')
]

FAILED = 0
PASSED = 0
for t in tests:

    # Set up the parts for the HTTP call
    ENDPOINT = t[0]
    URL = 'http://' + str(HOSTNAME, encoding) + ':' + PORT + ENDPOINT
    METHOD = t[1]
    STATUS = t[2]
    EXP_RESULT = t[3]

    # Determine which type of HTTP call to Make
    if METHOD == 'GET':
        resp = requests.get(URL)
    else:
        JSON_PAYLOAD = {'key': t[4], 'value': t[5]}
        if METHOD == 'POST':
            resp = requests.post(URL, json=JSON_PAYLOAD)
        else:
            resp = requests.put(URL, json=JSON_PAYLOAD)

    # Start printing the output for the test results
    print (" * ", ENDPOINT[:28], "... ".ljust(35-len(ENDPOINT[:28]))),

    # Check the HTTP status code first
    if resp.status_code in STATUS:

        # Get the result from the 'output' key in the JSON response
        _no_json = "Failed to locate output key"
        try:
            JSON_RESULT = resp.json().get('output', _no_json)
        except:
            JSON_RESULT = False

        # Check the tests array for the expected results
        if EXP_RESULT == None or JSON_RESULT == EXP_RESULT:
            print ("Pass")
            PASSED += 1
        else:
            print ("Fail")
            FAILED += 1

    # If the status code was not in the list of expected results
    else:
        print ("Fail")
        FAILED += 1

# Return a value to indicate success / failure
sys.exit(FAILED)
