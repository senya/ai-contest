#!/usr/bin/python3

import sys
import os
import shutil
import operator
import battlelib
import bb
import random
import operator
import itertools

import battle

b = bb.BaasBox('http://localhost:9000', '__robot', '123', '1234567890')

if __name__ == '__main__':
    shutil.rmtree('bb-move-dir')
    os.mkdir('bb-move-dir')

    v = battle.get_versions()
    for x in v:
        battle.load_strategy(x[0], x[1], 'bb-move-dir/' + x[0] + '.py')

    exit()
    users = [x[0] for x in v]
    with open('bb-move-dir/users', 'w') as f:
        f.write('\n'.join(users) + '\n')
