"""
Startup application
"""

import logging
from datetime import date

import requests
import sqlalchemy.exc
from flask import \
    Flask, \
    render_template, \
    jsonify, \
    request, \
    redirect, \
    url_for
from flask.json import JSONEncoder
from flask_cors import \
    CORS, \
    cross_origin
from flask_sqlalchemy import SQLAlchemy

import config
import form as custom_form

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://' \
                                        + config.mysql_config['user'] \
                                        + ':' \
                                        + config.mysql_config['password'] \
                                        + '@' \
                                        + config.mysql_config['host'] \
                                        + '/' \
                                        + config.mysql_config['db']
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = config.secret_key

db = SQLAlchemy(app)

cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'


class CustomJSONEncoder(JSONEncoder):
    """ Converting date to ISO format """
    def default(self, o):
        if isinstance(o, date):
            return o.isoformat()

        return super().default(o)


app.json_encoder = CustomJSONEncoder


class Book(db.Model):
    """ Book modeling class """
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    isbn_10 = db.Column(db.String(10), unique=True, nullable=True)
    isbn_13 = db.Column(db.String(13), unique=True, nullable=True)
    other_identifier = db.Column(db.String(45), unique=True, nullable=True)
    title = db.Column(db.String(255), nullable=False)
    published_date = db.Column(db.Date, nullable=False)
    page_count = db.Column(db.Integer)
    cover_link = db.Column(db.String(2048), nullable=False)
    language = db.Column(db.String(45), nullable=False)
    authors = db.Column(db.Text, nullable=False)


db.create_all()


@app.route('/')
def main():
    """ Route to home page """
    return render_template('index.html')


@app.route('/book', methods=['GET', 'POST'], strict_slashes=False)
def book():
    """ Function to operate on a new book entry """
    form = custom_form.BookForm(request.form, csrf_enabled=True)
    if request.method == 'GET':
        form = custom_form.BookForm()
        return render_template('book.html',
                               action='/book',
                               title='Dodawanie książki',
                               form=form)
    if not form.validate_on_submit():
        return render_template('book.html',
                               action='/book',
                               title='Dodawanie książki',
                               form=form)
    form_book = Book()
    form.populate_obj(form_book)

    if request.form.get('isbn_10').strip() == '':
        form_book.isbn_10 = None
    if request.form.get('isbn_13').strip() == '':
        form_book.isbn_13 = None
    if request.form.get('other_identifier').strip() == '':
        form_book.other_identifier = None

    db.session.add(form_book)
    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        return render_template(
            'error.html',
            message='Książka o takim numerze istnieje już w bazie'
        )
    return redirect(url_for('books'))


@app.route('/book/<identity>', methods=['GET', 'POST'], strict_slashes=False)
def edit_book(identity):
    """ Function that allows to edit book  """
    if request.method == 'GET':
        found_book = Book.query.get_or_404(identity)
        form = custom_form.BookForm(obj=found_book)

        return render_template('book.html',
                               action=f'/book/{identity}',
                               title=f'Edycja książki o numerze wpisu: {identity}',
                               form=form)
    form = custom_form.BookForm(request.form)
    if not form.validate_on_submit():
        return render_template('book.html',
                               action=f'/book/{identity}',
                               title=f'Edycja książki o numerze wpisu: {identity}',
                               form=form)

    authors = request.form.get('authors').split('\n')
    authors_nonblank = ''
    for author in authors:
        if author.strip() != '':
            authors_nonblank += author + '\n'
    authors_nonblank = authors_nonblank[:-1]

    edited_book = Book.query.get(identity)

    if request.form.get('isbn_10').strip() == '':
        edited_book.isbn_10 = None
    elif request.form.get('isbn_10') != edited_book.isbn_10:
        edited_book.isbn_10 = request.form.get('isbn_10')

    if request.form.get('isbn_13').strip() == '':
        edited_book.isbn_13 = None
    elif request.form.get('isbn_13') != edited_book.isbn_13:
        edited_book.isbn_13 = request.form.get('isbn_13')

    if request.form.get('other_identifier').strip() == '':
        edited_book.other_identifier = None
    elif request.form.get('other_identifier') != edited_book.other_identifier:
        edited_book.other_identifier = request.form.get('other_identifier')

    if request.form.get('title') != edited_book.title:
        edited_book.title = request.form.get('title')
    if request.form.get('published_date') != edited_book.published_date:
        edited_book.published_date = request.form.get('published_date')
    if request.form.get('page_count') != edited_book.page_count:
        edited_book.page_count = request.form.get('page_count')
    if request.form.get('cover_link') != edited_book.cover_link:
        edited_book.cover_link = request.form.get('cover_link')
    if request.form.get('language') != edited_book.language:
        edited_book.language = request.form.get('language')
    if authors_nonblank != edited_book.authors:
        edited_book.authors = authors_nonblank

    try:
        db.session.commit()
    except sqlalchemy.exc.IntegrityError:
        db.session.rollback()
        return render_template(
            'error.html',
            message='Książka o takim numerze istnieje już w bazie'
        )
    return render_template('success.html', message='Sukces edycji książki')


@cross_origin()
@app.route('/books', methods=['GET'], strict_slashes=False)
def books():
    """ Function for displaying a book list """
    return render_template('books.html')


@app.route('/get_books', methods=['GET'])
def get_books():
    """ Function that generates a json with a list of books """
    existing_books = db.session.query(Book).all()
    books_json = []
    for existing_book in existing_books:
        if hasattr(existing_book, '_sa_instance_state'):
            delattr(existing_book, '_sa_instance_state')

        books_json.append(existing_book.__dict__)
    response = jsonify(books_json)
    if len(books_json) > 0:
        response.status_code = 200
    else:
        response.status_code = 204
    return response


def customize_date(incomplete_date):
    """ Function for processing an incomplete date """
    if len(incomplete_date) == 4:
        return incomplete_date + '-01-01'
    if len(incomplete_date) == 7:
        return incomplete_date + '-01'
    return incomplete_date


@app.route('/import_books_new', methods=['GET', 'POST'])
def import_books_new():
    """ Function to parameterize the import """
    form = custom_form.ImportForm(request.form)
    if request.method == 'GET':
        form = custom_form.ImportForm()
        return render_template('import_new.html', form=form)
    if not form.validate_on_submit():
        return render_template('import_new.html', form=form)

    parameters = {}

    intitle = request.form.get('intitle')
    if intitle is not None and intitle != '':
        parameters['intitle'] = intitle

    inauthor = request.form.get('inauthor')
    if inauthor is not None and inauthor != '':
        parameters['inauthor'] = inauthor

    inpublisher = request.form.get('inpublisher')
    if inpublisher is not None and inpublisher != '':
        parameters['inpublisher'] = inpublisher

    subject = request.form.get('subject')
    if subject is not None and subject != '':
        parameters['subject'] = subject

    isbn = request.form.get('isbn')
    if isbn is not None and isbn != '':
        parameters['isbn'] = isbn

    lccn = request.form.get('lccn')
    if lccn is not None and lccn != '':
        parameters['lccn'] = lccn

    oclc = request.form.get('oclc')
    if oclc is not None and oclc != '':
        parameters['oclc'] = oclc

    filter_parameters = ''

    partial = request.form.get('partial')
    if partial is not None and partial == 'partial':
        filter_parameters += '&filter=partial'

    full = request.form.get('full')
    if full is not None and full == 'full':
        filter_parameters += '&filter=full'

    free_ebooks = request.form.get('free_ebooks')
    if free_ebooks is not None and free_ebooks == 'free_ebooks':
        filter_parameters += '&filter=free_ebooks'

    paid_ebooks = request.form.get('paid_ebooks')
    if paid_ebooks is not None and paid_ebooks == 'paid_ebooks':
        filter_parameters += '&filter=paid_ebooks'

    ebooks = request.form.get('ebooks ')
    if ebooks is not None and ebooks == 'ebooks ':
        filter_parameters += '&filter=ebooks'

    if len(parameters) > 0:
        parameters_list = 'q={}+'.format(request.form.get('q'))
    else:
        parameters_list = 'q={}'.format(request.form.get('q'))

    parameters_list += '+'.join(
        '{}:{}'.format(key, value) for key, value in parameters.items())
    parameters_list += filter_parameters

    response = requests.get(config.BOOKS_URL_NEW, params=parameters_list)

    if request.form.get('submit_button') == 'import':
        return import_to_database(response.json())
    return response.json()


def import_to_database(json_data):
    """ Function for importing books into the database """
    if 'items' in json_data:
        for item in json_data['items']:
            isbn_10 = None
            isbn_13 = None
            other_identifier = None
            for industry_identifier in item['volumeInfo'][
                'industryIdentifiers']:
                if industry_identifier['type'] == 'ISBN_10':
                    isbn_10 = industry_identifier['identifier']
                elif industry_identifier['type'] == 'ISBN_13':
                    isbn_13 = industry_identifier['identifier']
                else:
                    other_identifier = industry_identifier['identifier']

            authors = ''
            if 'authors' in item['volumeInfo']:
                for author in item['volumeInfo']['authors']:
                    authors += author + '\n'
                authors = authors[:-1]

            imported_book = Book(isbn_10=isbn_10,
                        isbn_13=isbn_13,
                        other_identifier=other_identifier,
                        title=item['volumeInfo']['title'],
                        published_date=customize_date(
                            item['volumeInfo']['publishedDate']),
                        page_count=item['volumeInfo'].get('pageCount'),
                        cover_link=item['volumeInfo']['previewLink'],
                        language=item['volumeInfo']['language'],
                        authors=authors
                        )
            db.session.add(imported_book)
            try:
                db.session.commit()
            except sqlalchemy.exc.IntegrityError:
                db.session.rollback()
                logging.warning('Ta książka istnieje już w bazie!')
    else:
        return render_template('error.html',
                               message='Brak rekordów o podanym zapytaniu')
    return render_template('success.html',
                           message='Udało się zaimportować dane do bazy')


if __name__ == '__main__':
    app.run(debug=True)
