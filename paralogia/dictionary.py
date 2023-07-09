from flask import Flask, jsonify, after_this_request

import sys 
import os
import re
import subprocess
import sqlite3
from pprint import pprint
import json
from jamdict import Jamdict
from sudachipy import tokenizer
from sudachipy import dictionary

from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from paralogia.auth import login_required
from paralogia.db import get_db

bp = Blueprint("dictionary", __name__)

PROJECT_ROOT = os.path.dirname(os.path.realpath(__file__))
EN_JA_DICTIONARY_DATABASE = os.path.join(PROJECT_ROOT, 'static', 'data', 'en-ja.sqlite3')
SENTENCES_DATABASE =  os.path.join(PROJECT_ROOT, 'static', 'data', 'sentences.db')



tokenizer_obj = dictionary.Dictionary().create()
jam = Jamdict()

con = sqlite3.connect(EN_JA_DICTIONARY_DATABASE,check_same_thread=False)
en_ja_cursor = con.cursor()

con2 = sqlite3.connect(SENTENCES_DATABASE,check_same_thread=False)
sentences_cursor = con2.cursor()


def get_example_sentences(search):
    global sentences_cursor

    search_results = 'not found'

    mode = tokenizer.Tokenizer.SplitMode.C
    modulizer = tokenizer_obj.tokenize(search,mode)[0]

    search_forms = []
    search_forms.append(search)

    if modulizer.part_of_speech()[0] == '形容詞':
        print('it is i-adjective')

        form = modulizer.dictionary_form()[:-1]
        form += 'く'
        search_forms.append(form)

        form = modulizer.dictionary_form()[:-1]
        form += 'か'
        search_forms.append(form)


    elif modulizer.part_of_speech()[0] == '動詞':
        print('it is a verb')

        stemma = modulizer.dictionary_form()[:-1]
        search_forms.append(stemma)


    for i in range(len(search_forms)):
        if i == 0:
            search_pattern = search_forms[i]
        else:
            search_pattern += '\|' + search_forms[i]
    
    print('pattern to look for: '+search_pattern)


    sentences_cursor.execute("SELECT * FROM sentences WHERE translation LIKE '%' || ? || '%'", (search_pattern,))
    query_result = sentences_cursor.fetchall()
    results_ready_to_go = dict()
    SENTENCE = 1
    TRANSLATION = 2
    for result in query_result:
        sentence = result[1]
        translation = result[2]
        results_ready_to_go[sentence] = translation

    return results_ready_to_go



    


def get_translations_en_ja(search):
    global en_ja_cursor
    en_ja_cursor.execute("SELECT * FROM translation_grouped WHERE written_rep = ?", (search,))

    query_result = en_ja_cursor.fetchall()

    search_results = dict()

    for i in query_result:
        search_results[i[3]] = i[4]

    results_ready_to_go = dict()
    results_ready_to_go['en_ja_results'] = search_results
    print(search)
    #print(results_ready_to_go)
    return results_ready_to_go


def get_translations_ja_en(search):
    print('your search '+search)
    search_results = []
    results = jam.lookup(search)
    for i in results.entries:
        i = re.sub(r'\[.*\]','',str(i))
        i = re.sub(r'\(\(.*\)\)','',str(i))
        search_results.append(str(i))
        
    search_results = list(search_results)
    return search_results


@bp.route('/dictionaryLookup', methods=['GET'])
@login_required
def dictionary_lookup():
    @after_this_request
    def add_header(response):
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    search = request.args.get('search')

    if search.isascii():
        search_results = get_translations_en_ja(search)

        if len(search_results['en_ja_results'].keys()) == 0:
            results_ready_to_go = dict()
            results_ready_to_go['en_ja_results'] = False
        else:
            results_ready_to_go = search_results

        results_ready_to_go['ja_en_results'] = False
        
        search_results = jsonify(results_ready_to_go)
        return search_results

    else:
        mode = tokenizer.Tokenizer.SplitMode.C
        m = tokenizer_obj.tokenize(search,mode)[0]

        if m.part_of_speech()[0] == '動詞':
            search = m.dictionary_form()

        search_results = get_translations_ja_en(search)

        if search_results:
            examples = get_example_sentences(search)
        else:
            examples = []


        results_ready_to_go = dict()
        results_ready_to_go['exampleSentences'] = examples

        if search_results:
            results_ready_to_go['ja_en_results'] = search_results
        else:
            results_ready_to_go['ja_en_results'] = False

        results_ready_to_go['en_ja_results'] = False

        search_results = jsonify(results_ready_to_go)
        return search_results
