import json
from unittest.mock import patch

import requests
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

from app import db
import app
import config
import unittest


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.app = Flask(__name__)
        self.app.testing = True
        self.app.config[
            'SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/{}'.format(
            config.postgres_config['user'],
            config.postgres_config['password'],
            config.postgres_config['host'],
            config.postgres_config['db']
        )
        db.init_app(self.app)
        self.db = db

        self.client = app.app.test_client()

        with self.app.app_context():
            db.create_all()

    def tearDown(self):
        self.app = Flask(__name__)
        self.app.config[
            'SQLALCHEMY_DATABASE_URI'] = 'mysql://{}:{}@{}/{}'.format(
            config.postgres_config_test['user'],
            config.postgres_config_test['password'],
            config.postgres_config_test['host'],
            config.postgres_config_test['db']
        )
        db.init_app(self.app)
        with self.app.app_context():
            db.drop_all()

    def test_invalid_route(self):
        test_response = self.client.get('/wrong_route')
        assert test_response.status_code == 404

    def test_main_route(self):
        test_response = self.client.get('/')
        assert test_response.status_code == 200

    def test_book_route(self):
        test_response = self.client.get('/book')
        assert test_response.status_code == 200

        test_response = self.client.get('/book/')
        assert test_response.status_code == 200

    def test_edit_book_route(self):
        book = db.session.query(func.max(app.Book.id)).one()[0]

        if book is not None:
            test_response = self.client.get('/book/{}'.format(book))
            assert test_response.status_code == 200

            test_response = self.client.get('/book/')
            assert test_response.status_code == 200

            book += 1
            test_response = self.client.get('/book/{}'.format(book))
            assert test_response.status_code == 404

    def test_books_route(self):
        test_response = self.client.get('/books')
        assert test_response.status_code == 200

        test_response = self.client.get('/books/')
        assert test_response.status_code == 200

    def test_get_books_route(self):
        books = db.session.query(app.Book).all()
        test_response = self.client.get('/get_books')

        if len(books) > 0:
            assert test_response.status_code == 200
        else:
            assert test_response.status_code == 204

        test_response = self.client.get('/get_books/')
        assert test_response.status_code == 404

    def test_customize_date(self):
        year = '2010'
        without_day = '2011-12'
        full = '1990-12-02'
        assert len(app.customize_date(year)) == 10
        assert len(app.customize_date(without_day)) == 10
        assert len(app.customize_date(full)) == 10

    def test_import_books_new_route(self):
        test_response = self.client.get('/import_books_new')
        assert test_response.status_code == 200

        test_response = self.client.get('/import_books_new/')
        assert test_response.status_code == 404


if __name__ == '__main__':
    unittest.main()
