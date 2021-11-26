"""
Project configuration file
"""

import secrets

postgres_config = dict(user='postgres',
                       password='',
                       db='library',
                       host='localhost',
                       port=5432)
postgres_config_test = dict(user='postgres',
                            password='',
                            db='library_Test',
                            host='localhost',
                            port=5432)
secret_key = secrets.token_urlsafe(16)
BOOKS_URL = 'https://www.googleapis.com/books/v1/volumes?q=Hobbit'

BOOKS_URL_NEW = 'https://www.googleapis.com/books/v1/volumes?'
