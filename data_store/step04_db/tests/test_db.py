import os
import tempfile
from unittest import TestCase

from ..db import DB


class DBTest(TestCase):
    def setUp(self):
        self.filename = tempfile.mktemp()
        self.db = DB(self.filename)

    def tearDown(self):
        self.db.close()
        os.unlink(self.filename)

    def test_get_invalid_key(self):
        with self.assertRaises(KeyError):
            self.db['k']

    def test_get_set(self):
        self.db['k1'] = 'v1'
        self.db['k2'] = 'v2'

        self.assertEqual('v2', self.db['k2'])
        self.assertEqual('v1', self.db['k1'])

    def test_del(self):
        self.db['k'] = 'v'
        del self.db['k']
        with self.assertRaises(KeyError):
            self.db['k']

    def test_set_no_transaction(self):
        self.db['k1'] = 'v1'
        self.db['k2'] = 'v2'
        self.assertEqual(2, self.db.commit_times)

    def test_set_transaction(self):
        with self.db.begin_transaction() as transaction:
            self.db['k1'] = 'v1'
            self.db['k2'] = 'v2'
            transaction.commit()

        self.assertIsNone(self.db.transaction)
        self.assertEqual(1, self.db.commit_times)
        self.assertEqual('v2', self.db['k2'])
        self.assertEqual('v1', self.db['k1'])

