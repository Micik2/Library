"""
Contains fields contained in forms along with server validation
"""

from flask_wtf import FlaskForm
from wtforms import \
    StringField, \
    DateField, \
    IntegerField, \
    TextAreaField
from wtforms.validators import \
    DataRequired, \
    Length, \
    Regexp, \
    URL, \
    Optional

VALIDATION_INFO_BASIC = 'Pole wymagane'
VALIDATION_INFO_INTEGER = 'Pole może się składać wyłącznie z cyfr'
VALIDATION_INFO_WHITESPACES = 'Pole nie może zawierać wyłącznie białych znaków'


class BookForm(FlaskForm):
    """ Form for a book Class """
    isbn_10 = StringField('ISBN10', validators=[
        Length(max=10, message='Pole może zawierać maksymalnie 10 cyfr')])
    isbn_13 = StringField('ISBN13', validators=[
        Length(max=13, message='Pole może zawierać maksymalnie 13 cyfr')])
    other_identifier = StringField('Inny identyfikator książki')
    title = StringField('Tytuł', validators=[
        DataRequired(message=VALIDATION_INFO_BASIC),
        Regexp(regex=r'.*[^\s].*', message=VALIDATION_INFO_WHITESPACES)])
    published_date = DateField('Data publikacji', validators=[
        DataRequired(message=VALIDATION_INFO_BASIC)])
    page_count = IntegerField('Liczba stron', validators=[Optional()])
    cover_link = StringField('Link do okładki', validators=[
        DataRequired(message=VALIDATION_INFO_BASIC),
        URL(message='Pole musi zawierać poprawny adres URL')])
    language = StringField('Język', validators=[
        DataRequired(message=VALIDATION_INFO_BASIC),
        Length(min=2,
               message='Oznaczenie języka musi zawierać minimum 2 znaki'),
        Regexp(regex=r'.*[^\s].*', message=VALIDATION_INFO_WHITESPACES)])
    authors = TextAreaField('Autorzy', validators=[
        Regexp(regex=r'.*[^\s].*', message=VALIDATION_INFO_WHITESPACES)])


ADDITIONAL_INFO = 'Zwraca wyniki, '


class ImportForm(FlaskForm):
    """ Form for import view """
    q = StringField('Zapytanie',
                    validators=[
                        DataRequired(
                            message=VALIDATION_INFO_BASIC
                        ),
                        Regexp(
                            regex=r'.*[^\s].*',
                            message=VALIDATION_INFO_WHITESPACES
                        )]
                    )
    intitle = StringField('Tytuł')
    inauthor = StringField('Autor')
    inpublisher = StringField('Wydawca')
    subject = StringField('Temat')
    isbn = StringField('ISBN')
    lccn = StringField('Numer kontrolny Biblioteki Kongresu')
    oclc = StringField('Numer Centrum Bibliotek Komputerowych Online')
