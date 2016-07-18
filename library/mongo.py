#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
try:
    import pymongo
except ImportError:
    print('{"msg": "Error: pymongo is required", "failed": true}')
    sys.exit(1)

from ansible.module_utils.basic import *


class Mongo:
    def __init__(self, module):
        self.module = module
        self.host = module.params['host']
        self.port = module.params['port']
        self.user = module.params['user']
        self.password = module.params['password']
        self.database = module.params['database']
        self.collection = module.params['collection'].replace('.', '_')
        self.query = module.params['query']
        self.update = module.params['update']
        self._init_db()

    def _init_db(self):
        cli = pymongo.MongoClient(host=self.host, port=self.port)
        try:
            cli.server_info()
        except pymongo.errors.ServerSelectionTimeoutError:
            print('{"msg": "Can not connect to mongo server", "failed": true}')
            sys.exit(1)

        db = cli[self.database]
        if self.user:
            try:
                db.authenticate(self.user, self.password)
            except pymongo.errors.OperationFailure:
                print('{"msg": "username / password are incorrect", "failed": true}')
                sys.exit(1)

        [setattr(self, c.replace('.', '_'), db[c]) for c in db.collection_names() if c]

    def find_one(self):
        return getattr(self, self.collection).find_one(self.query)

    def update_one(self):
        return getattr(self, self.collection).update_one(self.query, self.update)


def main():
    module = AnsibleModule(
        argument_spec=dict(
            host=dict(default='127.0.0.1', type='str'),
            port=dict(default=27017, type='int'),
            user=dict(default=None, type='str'),
            password=dict(default=None, no_log=True),
            database=dict(default='meteordb', type='str'),
            collection=dict(default='vms', type='str'),
            query=dict(default={}, type='dict'),
            update=dict(default={}, type='dict'),
            action=dict(default='find', type='str')
        )
    )

    mongo = Mongo(module)

    if module.params['action'] == 'find':
        ret = mongo.find_one()
        module.exit_json(**ret)

    elif module.params['action'] == 'update':
        ret = mongo.update_one()
        module.exit_json(**ret.raw_result)


if __name__ == '__main__':
    main()
