#!/usr/bin/env python
import os
import sys

from step04_db.db import DB


def usage():
    print('Usage:')
    print('\t./cli.py <DBNAME> get <KEY>         - get value')
    print('\t./cli.py <DBNAME> set <KEY> <VALUE> - set key value')
    print('\t./cli.py <DBNAME> del <KEY>         - delete key')
    print('\t./cli.py <DBNAME> purge             - delete database')


def _get(db: DB, key):
    print('{} => {}'.format(key, db[key]))


def _set(db: DB, key, value):
    db[key] = value


def _del(db: DB, key):
    del db[key]


def _purge(db: DB):
    pass


def _purge(db: DB):
    filename = db._storage._f.name
    db.close()
    os.unlink(filename)


def main(argv):
    try:
        if not (2 <= len(argv) <= 4):
            raise SyntaxError()
        db_name, op = argv[0], argv[1]
        db = DB(db_name)
        ops = {
            'get': _get,
            'set': _set,
            'del': _del,
            'purge': _purge,
        }
        if op not in ops:
            raise SyntaxError()
        ops[op](db, *argv[2:])
        return 0
    except (SyntaxError, TypeError):
        import traceback
        traceback.print_exc()
        usage()
        return -1


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
