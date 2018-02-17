import operator
import itertools
import dateutil
from collections import defaultdict

from flask import Flask, request, send_from_directory, jsonify
from celery import Celery


import battle

import bb

b = bb.BaasBox('http://localhost:9000', '__robot', '123', '1234567890')


app = Flask(__name__)
print(app.name)

broker_uri = 'amqp://guest@localhost'
celery = Celery(app.name, broker=broker_uri)

@celery.task(bind=True)
def do_battle(self, user1, version1, user2, version2, system):
    battle.battle(user1, version1, user2, version2, system)

@app.route("/")
def hello():
    return app.send_static_file('index.html')

@app.route("/login")
def login():
    return app.send_static_file('login.html')

@app.route("/player")
def player():
    return app.send_static_file('svg.htm')

@app.route("/js/<path:path>")
def send_js(path):
    return send_from_directory('js', path)

@app.route("/css/<path:path>")
def send_css(path):
    return send_from_directory('css', path)

@app.route('/battle', methods=['POST'])
def contest():
    f = request.form
    #return str(request.form['user1'])
    #return battle.battle(f['user1'], int(f['version1']), f['user2'], int(f['version2']), False)
    do_battle.delay(f['user1'], int(f['version1']), f['user2'], int(f['version2']), False)
    return 'ok'

@app.route('/get_versions', methods=['POST', 'GET'])
def get_versions():
    key=operator.itemgetter('user')
    files = itertools.groupby(sorted(b.files(), key=key), key=key)

    res = {}
    for k, g in files:
        if k != '__robot':
            res[k] = len(list(g))

    return jsonify(res)

@app.route('/get_results', methods=['POST', 'GET'])
def get_results():
    global b
    battles = b.documents('battles', {'where': 'body.system=true'})
    users = defaultdict(list)
    for bat in battles:
        timestamp = dateutil.parser.parse(bat['_creation_date']).timestamp()
        users[bat['body']['user1']].append((timestamp, bat['body']['points1']))
        users[bat['body']['user2']].append((timestamp, bat['body']['points2']))

    results = []
    for name in users:
        ar = sorted(users[name])[-15:]
        mean = sum([x[1] for x in ar]) / len(ar)
        results.append({'name': name, 'mean': mean})

    results.sort(key=operator.itemgetter('mean'))

    return jsonify(list(reversed(results)))
