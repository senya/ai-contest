#!/usr/bin/python3

import sys
import os
import operator
import battlelib
import bb
import random
import operator
import itertools

# For this to work you should have pwddd.py file with content like
# pwd = '12345'
import pwddd

b = bb.BaasBox('http://localhost:9000', '__robot', pwddd.pwd, '1234567890')

def get_strategy(user, version):
    files = b.files_raw({'where': "_author == '" + user + "'", 'orderBy': '_creation_date asc'})
    assert version <= len(files)
    return files[version - 1]

def load_strategy(user, version, file_name):
    files = b.files_raw({'where': "_author == '" + user + "'", 'orderBy': '_creation_date asc'})
    assert version <= len(files)
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

    print(battle)
    return b.create_document('battles', battle)

def get_versions():
    res = []
    for u in b.users():
        cnt = b.files_raw({'where': "_author == '" + u + "'", 'count': True})[0]['count']
        if cnt:
            res.append((u, cnt))

    return res

def systembattle():
    ar = get_versions()
    if len(ar) < 2:
        return '< 2 users'

    i, j = random.sample(range(len(ar)), 2)

    return battle(ar[i][0], ar[i][1], ar[j][0], ar[j][1], True)

def tournaiment():
    ar = get_versions()
    if len(ar) < 2:
        return '< 2 users'

    total = 10 * len(ar) * (len(ar) - 1) // 2
    done = 0
    for i in range(len(ar) - 1):
        for j in range(i + 1, len(ar)):
            for k in range(5):
                print(battle(ar[i][0], ar[i][1], ar[j][0], ar[j][1], True))
                done += 1
                print('DONE ', done, '/', total)
            for k in range(5):
                print(battle(ar[j][0], ar[j][1], ar[i][0], ar[i][1], True))
                done += 1
                print('DONE ', done, '/', total)


if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        print(battle(sys.argv[1], int(sys.argv[2]), sys.argv[3], int(sys.argv[4]), False))
    else:
        tournaiment()
        #print(systembattle())
