#!/usr/bin/env python3

import os
import sys
import re

import MySQLdb
import MySQLdb.cursors
import MySQLdb.constants.ER


class DBConn:
    from configparser import ConfigParser
    cfp = ConfigParser(allow_no_value=True)
    cfp.read(os.path.expanduser('~/.my.cnf'))

    def __init__(self, dbname, cursortype=MySQLdb.cursors.Cursor, noisy=False):
        db = dict(DBConn.cfp.items(dbname))
        self.conn = MySQLdb.connect(db['host'], db['user'],
                                    db['password'], db['database'])
        self.cursor = self.conn.cursor(cursortype)
        self.noisy = noisy

    # pass thru calls to cursor
    def __getattr__(self, attr):
        try:
            return object.__getattr__(self, attr)
        except AttributeError:
            return getattr(self.cursor, attr)

    def execute(self, *args, **kwargs):
        while True:
            try:
                if self.noisy:
                    argstr = ', ' + str(args[1]) if len(args) > 1 else ''
                    print(re.sub(r' +', ' ', args[0]) + argstr)
                self.cursor.execute(*args, **kwargs)
                return self
            except MySQLdb.OperationalError as e:
                if e.args[0] == MySQLdb.constants.ER.NET_READ_INTERRUPTED:
                    print('Stupid ass DB timed out. Retrying.',
                          file=sys.stderr)
                else:
                    raise
