"""
Project configuration file
"""

import secrets

mysql_config = dict(user='root',
                    password='54ImKBAF5Z8aXk8G',
                    db='Library',
                    host='localhost')
mysql_config_test = dict(user='root',
                         password='54ImKBAF5Z8aXk8G',
                         db='Library_Test',
                         host='localhost')
secret_key = secrets.token_urlsafe(16)
BOOKS_URL = 'https://www.googleapis.com/books/v1/volumes?q=Hobbit'

BOOKS_URL_NEW = 'https://www.googleapis.com/books/v1/volumes?'
