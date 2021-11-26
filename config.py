"""
Project configuration file
"""

import secrets

postgres_config = dict(user='hidden',
                       password='hidden',
                       db='hidden',
                       host='hidden',
                       port=5432)
postgres_config_test = dict(user='hidden',
                            password='hidden',
                            db='hidden',
                            host='hidden',
                            port=5432)
secret_key = secrets.token_urlsafe(16)
BOOKS_URL = 'https://www.googleapis.com/books/v1/volumes?q=Hobbit'

BOOKS_URL_NEW = 'https://www.googleapis.com/books/v1/volumes?'
