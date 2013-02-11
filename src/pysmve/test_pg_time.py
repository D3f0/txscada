'''
Database timestamp check for microsecond resolution
'''

from unittest import TestCase, main as run_test
from psycopg2 import connect, OperationalError
from fabric.api import local
from datetime import datetime


def dropdb(name):
    '''Drop database'''
    local('dropdb %s' % name)


def createdb(name, drop_if_exists=True):
    '''Create database'''
    if drop_if_exists:
        try:
            connect('dbname=%s' % name)
        except OperationalError:
            pass  # DB does not exists
        else:
            dropdb(name)
    local('createdb %s' % name)


class TestPostgresTimeResolution(TestCase):
    def setUp(self):
        self.dbname = 'pysmve_test_foo'
        createdb(self.dbname)
        self.connection = connect('dbname={}'.format(self.dbname))
        self.cursor = self.connection.cursor()

        self.cursor.execute('''
            CREATE TABLE timestamp_table (
                timestamp_row timestamp
            )
        ''')

    def test_timestam_has_resolution_under_second(self):
        test_inserted_value = datetime(2012, 1, 1, 0, 0, 0, 123456)
        self.cursor.execute('''
            INSERT INTO timestamp_table (timestamp_row) VALUES
            (%s)
        ''', [test_inserted_value, ])
        self.cursor.execute('SELECT * FROM timestamp_table')
        data = self.cursor.fetchone()
        timestamp = data[0]
        self.assertEqual(timestamp.microsecond, test_inserted_value.microsecond,
            "Database timestamp microsecond should match with inserted")

    def tearDown(self):
        self.cursor.close()
        self.connection.close()
        dropdb(self.dbname)


if __name__ == '__main__':
    run_test()
