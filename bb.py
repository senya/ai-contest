#!/usr/bin/env python3

import requests
import dateutil.parser
import shutil
import operator
import itertools
import datetime
import json
import time

class BaasBox:
    def __init__(self, addr, login, password, appcode):
        self._addr = addr if addr[-1] == '/' else addr + '/'
        self._session = requests.Session()

        r = self._session.post(self._addr + 'login', data={
                'username': login,
                'password': password,
                'appcode': appcode
            })

        self._session.headers.update({'X-BB-SESSION': r.json()['data']['X-BB-SESSION']})


    def create_json_file(self, name, doc):
        #self._session.headers.update({'Content-type': 'application/json'})
        files = {'file': (name, json.dumps(doc))}
        r = self._session.post(self._addr + 'file', files=files).json()
        assert r['result'] == 'ok'
        print('file: ', r['data']['id'])
        fid = r['data']['id']
        r = self._session.put(self._addr + 'file/' + fid + '/read/role/anonymous').json()
        print(r)
        assert r['result'] == 'ok'
        return fid

    def create_document(self, collection, doc):
        r = self._session.post(self._addr + 'document/' + collection, data=json.dumps({'body': doc}), headers={'Content-type': 'application/json'}).json()
        assert r['result'] == 'ok'
        id = r['data']['id']
        print(id)

        r = self._session.put(self._addr + 'document/' + collection + '/' + id + '/read/role/anonymous').json()
        assert r['result'] == 'ok'

        return id

    def documents(self, collection, data):
        r = self._session.get(self._addr + 'document/' + collection, params=data).json()
        assert r['result'] == 'ok'
        return r['data']

    def get(self, relative, **kwargs):
        return self._session.get(self._addr + relative, **kwargs)


    def delete(self, relative, **kwargs):
        return self._session.delete(self._addr + relative, **kwargs)


    def get_json(self, relative):
        return self._session.get(self._addr + relative).json()['data']
    
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

    def save_file(self, id, path):
        r = self.get('file/' + id, stream=True)
        r.raw.decode_content = True
        with open(path, 'wb') as f:
            shutil.copyfileobj(r.raw, f)


    def revoke(self, id, action, user):
        self.delete('file/' + id + '/' + action + '/user/' + user)


if __name__ == '__main__':
    import sys

    b = BaasBox('http://localhost:9000', '__robot', '123', '1234567890')
    
    if len(sys.argv) > 2:
        b.save_file(sys.argv[1], sys.argv[2])
    else:
        kf = operator.itemgetter('user')
        for k, g in itertools.groupby(sorted(b.files(), key=kf), key=kf):
            print(k)
            for i, f in enumerate(sorted(g, key=operator.itemgetter('timestamp'))):
                date = datetime.datetime.fromtimestamp(f['timestamp']).strftime('%d.%m.%Y %H:%M')
                print('  ', i + 1, f['name'], date, f['id'])
