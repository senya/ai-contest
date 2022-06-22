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

b = bb.BaasBox('http://localhost:9000', '__robot', 'sin20', '1234567890')

if __name__ == '__main__':

    #[print(u) for u in b.users()]
    #exit()
    vv = battle.get_versions()
    for u, v in vv:
        s = battle.get_strategy(u, v)
        print(u, v, s['_creation_date'], s['fileName'])
    exit()
    for x in vv:
        print(x[0], x[1])
        for i in range(1, x[1] + 1):
            s = battle.get_strategy(x[0], i)
            print(' ', i, ' > ', s['_creation_date'])
