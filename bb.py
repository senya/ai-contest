#!/usr/bin/env python3

import requests
import dateutil.parser
import shutil
import operator
import itertools
import datetime
import dateutil
import simplejson as json
import time
import re
from decimal import Decimal

def pretty_floats(obj):
    if isinstance(obj, float):
        return Decimal('%.2f' % obj)
    elif isinstance(obj, dict):
        return dict((k, pretty_floats(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return list(map(pretty_floats, obj))
    return obj

class BaasBox:
    def __init__(self, addr, login, password, appcode):
        self._addr = addr if addr[-1] == '/' else addr + '/'
        self._login = login
        self._password = password
        self._appcode = appcode

        self.connect()

    def connect(self):
        tries = 3
        for i in range(tries):
            if i != 0:
                print("can't connect, will retry, wait 5 seconds")
                time.sleep(5)

            self._session = requests.Session()
            r = self._session.post(self._addr + 'login', data={
                    'username': self._login,
                    'password': self._password,
                    'appcode': self._appcode
                })

            if r.status_code == 200:
                break

        assert r.status_code == 200

        self._session.headers.update({'X-BB-SESSION': r.json()['data']['X-BB-SESSION']})

    def post(self, relative, **args):
        r = self._session.post(self._addr + relative, **args)

        if r.status_code not in (200, 201):
            self.connect()
            r = self._session.post(self._addr + relative, **args)

        assert r.status_code in (200, 201)
        r = r.json()
        assert r['result'] == 'ok'

        return r

    def get(self, relative, **args):
        r = self._session.get(self._addr + relative, **args)

        if r.status_code != 200:
            self.connect()
            r = self._session.get(self._addr + relative, **args)

        assert r.status_code == 200

        return r

    def create_json_file(self, name, doc):
        #self._session.headers.update({'Content-type': 'application/json'})

        files = {'file': (name, json.dumps(pretty_floats(doc)))}
        r = self.post('file', files=files)
        assert r['result'] == 'ok'
        print('file: ', r['data']['id'])
        fid = r['data']['id']
        r = self._session.put(self._addr + 'file/' + fid + '/read/role/anonymous').json()
        print(r)
        assert r['result'] == 'ok'
        return fid

    def create_document(self, collection, doc):
        r = self.post('document/' + collection, data=json.dumps({'body': doc}), headers={'Content-type': 'application/json'})
        assert r['result'] == 'ok'
        id = r['data']['id']
        print(id)

        r = self._session.put(self._addr + 'document/' + collection + '/' + id + '/read/role/anonymous').json()
        assert r['result'] == 'ok'

        return id

    def documents(self, collection, data):
        r = self.get('document/' + collection, params=data).json()
        assert r['result'] == 'ok'
        return r['data']


    def delete(self, relative, **kwargs):
        return self._session.delete(self._addr + relative, **kwargs)


    def get_json(self, relative, **kwargs):
        r = self.get(relative, **kwargs).json()
        assert r['result'] == 'ok'
        return r['data']
    
    def files(self):
        arr = self.get_json('file/details')
        ret = []
        for f in arr:
            ret.append({
                'id': f['id'],
                'timestamp': dateutil.parser.parse(f['_creation_date']).timestamp(),
                'user': f['_author'],
                'name': f['fileName']
            })
        return ret

    def files_raw(self, data):
        return self.get_json('file/details', params=data)

    def users(self):
        r = self.get_json('users', params={
                'fields': 'user.name',
                'where': "user.name <> '__robot'"
            })
        reg = '^[0-9]+_[a-zA-Z_0-9]+$'
        reg = '^[0-9]{3,4}_[a-zA-Z_0-9]+$'
        return [x['user'] for x in r]# if re.match(reg, x['user'])]

    def save_file(self, id, path):
        r = self.get('file/' + id, stream=True)
        r.raw.decode_content = True
        with open(path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


    def revoke(self, id, action, user):
        self.delete('file/' + id + '/' + action + '/user/' + user)


if __name__ == '__main__':
    import sys

    b = BaasBox('http://localhost:9000', '__robot', 'sin20', '1234567890')

    #print(b.files_raw({'page': 1, 'recordsPerPage': 10, 'where': 'contentLength > 200000'}))
    #exit()
    if len(sys.argv) > 2:
        b.save_file(sys.argv[1], sys.argv[2])
        exit()

    yes = datetime.date.today() - dateutil.relativedelta.relativedelta(days=1)
    x = 0
    page = 0
    while True:
    #for i in range(1):
        ff = b.documents('battles', {'page': page, 'recordsPerPage': 1})
        if not ff:
            print("nothing")
            break

        for f in ff:
            d = dateutil.parser.parse(f['_creation_date']).date()

            if d < yes or True:
                if 'record_id' in f['body']:
                    b.delete('file/' + f['body']['record_id'])
                else:
                    print('strange:', f)
                b.delete('document/battles/' + f['id'])
                x += 1
                print('deleted: ' + str(x))
            else:
                page += 1
                print('not deleted: ' + str(page) + ' ' + str(f))
    
    exit()
    
    if len(sys.argv) > 2:
        b.save_file(sys.argv[1], sys.argv[2])
    else:
        kf = operator.itemgetter('user')
        for k, g in itertools.groupby(sorted(b.files(), key=kf), key=kf):
            print(k)
            for i, f in enumerate(sorted(g, key=operator.itemgetter('timestamp'))):
                date = datetime.datetime.fromtimestamp(f['timestamp']).strftime('%d.%m.%Y %H:%M')
                print('  ', i + 1, f['name'], date, f['id'])
