from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from flask import session

from werkzeug.exceptions import abort

from paralogia.auth import login_required
from paralogia.db import get_db

import os
from os import listdir

import json



bp = Blueprint("paralogia", __name__)

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))

BOOKS = os.path.join(PROJECT_ROOT, 'static', 'books')

DECKS = os.path.join(PROJECT_ROOT, 'static', 'decks')






@bp.route("/")
def index():

    if g.user:
        return render_template("paralogia/dashboard.html", username=g.user['username'])
    else:
        return render_template("paralogia/index.html")


@bp.route('/user_settings')
@login_required
def user_settings():
    return render_template("paralogia/user_settings.html",username=g.user['username'])



@bp.route('/reader')
@login_required
def reader():
    return render_template("paralogia/reader.html")

@bp.route("/readerSubmission", methods=["POST"])
@login_required
def reader_submission():
    text = request.form['text']
    lines = text.split('\n')

    return render_template("paralogia/library.html",bookTitle="Reader Mode",bookContent=lines)


@bp.route('/getLibraryBooks')
@login_required
def get_books():
    books = [book for book in listdir(BOOKS)]
    book_dict = dict()
    for i in range(len(books)):
        title = books[i].split('-')[0]
        translation = books[i].split('-')[1]
        book_dict[i] = {'title':title, 'translation':translation}
    return book_dict

@bp.route('/library')
@login_required
def library():
    title = request.args.get('book').split('-')[0]
    title_translation = request.args.get('book').split('-')[1]

    books = [book for book in listdir(BOOKS)]
    for book in books:
        if book == request.args.get('book'):
            BOOKPATH = os.path.join(BOOKS,book)
            with open(BOOKPATH,'r') as file:
                lines = [line.rstrip() for line in file]
            return render_template("paralogia/library.html",bookTitle=title,bookTitleTranslation=title_translation,bookContent=lines)

    return 'Invalid book name.'





@bp.route('/getDecks')
@login_required
def get_decks():
    decks = [deck for deck in listdir(DECKS)]
    deck_dict = dict()
    for i in range(len(decks)):
        title = decks[i].split('.')[0]
        deck_dict[i] = {'title':title}
    return deck_dict



@bp.route('/memorizer')
@login_required
def memorizer():

    requested_deck = request.args.get('deck')
    requested_deck += ".json"
    decks = [deck for deck in listdir(DECKS)]

    for deck in decks:
        if deck == requested_deck:
            DECKPATH = os.path.join(DECKS,deck)
            deck = open(DECKPATH)
            deck = json.load(deck)
            return render_template("paralogia/memorizer.html",deck=deck)
    
    return 'Invalid deck name.'



@bp.route('/practice',methods=['GET'])
@login_required
def practice():
    topic = request.args.get('topic')
    if topic == 'verbs':
        return render_template("paralogia/practice/verbs_practice.html")
    if topic == 'counters':
        return render_template("paralogia/practice/counters_practice.html")
    if topic == 'kana':
        return render_template("paralogia/practice/kana_practice.html")
    if topic == 'kanji':
        return render_template("paralogia/practice/kanji_practice.html")
