#!/usr/bin/python3

import sys
import os
import operator
import battlelib
import bb
import random
import operator
import itertools

b = bb.BaasBox('http://localhost:9000', '__robot', '123', '1234567890')

def load_strategy(user, version, file_name):
    files = [f for f in b.files() if f['user'] == user]
    assert version <= len(files)
    files.sort(key=operator.itemgetter('timestamp'))
    b.save_file(files[version - 1]['id'], file_name)

def battle(user1, version1, user2, version2, system):
    print(user1, version1, user2, version2, system)
    load_strategy(user1, version1, 'user1.py')
    load_strategy(user2, version2, 'user2.py')
    p1_p, p2_p, json = battlelib.battle(user1, 'user1.py', user2, 'user2.py', 5000)
    os.remove('user1.py')
    os.remove('user2.py')

    if p1_p < p2_p:
        user1, user2 = user2, user1
        version1, version2 = version2, version1
        p1_p, p2_p = p2_p, p1_p

    battle = {
        'system': system,
        'user1': user1,
        'version1': version1,
        'points1': p1_p,
        'user2': user2,
        'version2': version2,
        'points2': p2_p,
        'record_id': b.create_json_file('mega', json) 
    }

    return b.create_document('battles', battle)

def get_versions():
    key=operator.itemgetter('user')
    files = itertools.groupby(sorted(b.files(), key=key), key=key)

    res = []
    for k, g in files:
        if k != '__robot':
            res.append((k, len(list(g))))

    return res

def systembattle():
    ar = get_versions()
    i, j = random.sample(range(len(ar)), 2)

    return battle(ar[i][0], ar[i][1], ar[j][0], ar[j][1], True)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        print(battle(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), False))
    else:
        print(systembattle())
