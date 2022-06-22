import operator
import itertools
import dateutil
from collections import defaultdict

from flask import Flask, request, send_from_directory, jsonify
from celery import Celery

import pwddd

import battle

import bb

b = bb.BaasBox('http://localhost:9000', '__robot', pwddd.pwd, '1234567890')


app = Flask(__name__)

broker_uri = 'amqp://guest@localhost'
celery = Celery(app.name, broker=broker_uri)

#@celery.task(bind=True)
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

@app.route("/pubpy/<path:path>")
def send_pubpy(path):
    return send_from_directory('pubpy', path)

#@app.route('/battle', methods=['POST'])
def contest():
    f = request.form
    #return str(request.form['user1'])
    #return battle.battle(f['user1'], int(f['version1']), f['user2'], int(f['version2']), False)
    do_battle.delay(f['user1'], int(f['version1']), f['user2'], int(f['version2']), False)
    return 'ok'

@app.route('/get_versions', methods=['POST', 'GET'])
def get_versions():
    res = {}
    for u in b.users():
        x = b.files_raw({'where': "_author == '" + u + "'", 'count': True})
        cnt = x[0]['count']
        if cnt:
            res[u] = cnt

    return jsonify(res)

#@app.route('/get_results', methods=['POST', 'GET'])
def get_results():
    results = []

    for u in b.users():
        d = b.documents('battles', {'where': "body.system=true and (body.user1='" + u + "' or body.user2='" + u + "')", 'page': 0, 'recordsPerPage': 20, 'orderBy': '_creation_date desc'})

        if not d:
            continue

        points = [x['body']['points1'] if x['body']['user1'] == u else x['body']['points2'] for x in d]

        results.append({'name': u, 'mean': sum(points) / len(points)})

    results.sort(key=operator.itemgetter('mean'))

    return jsonify(list(reversed(results)))

@app.route('/get_results2', methods=['POST'])
def get_results2():
    f = request.form
    show_all = 'show_all' in f and f['show_all'] == 'true'

    results = []

    d = b.documents('battles', {})
    hh = defaultdict(lambda: defaultdict(int))
    for x in d:
        if not show_all:
            if x['body']['user1'][0] not in '67' or x['body']['user2'][0] not in '67':
                continue
        if x['body']['points1'] > x['body']['points2']:
            hh[x['body']['user1']][x['body']['user2']] += 1

    for u1 in hh:
        wins = 0
        for u2 in hh:
            if hh[u1][u2] > 5:
                wins += 1
        results.append({'name': u1, 'wins': wins})

    results.sort(key=operator.itemgetter('wins'))
    results.reverse()
    for r in results:
        print(r)
    names = [r['name'] for r in results]

    tab = [['user', 'wins'] + names]
    for x in results:
        n = x['name']
        row = [n, x['wins']]
        for n2 in names:
            if n == n2:
                row.append('-')
            else:
                row.append('%d:%d' % (hh[n][n2], hh[n2][n]))
        tab.append(row)

    return jsonify(tab)

if __name__ == '__main__':
    jsonify = lambda x: x
    #print(get_versions())
    print(get_results2())
