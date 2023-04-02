import http

import flask

from app import instance
from server import app


@app.route('/api/sensitive', methods=['GET', 'PUT', 'DELETE'])
def handle_sensitive():
    id_ = flask.request.args.get('id', type=int)
    if id_ is None:
        return flask.make_response('error: missing id query', http.HTTPStatus.BAD_REQUEST)

    if flask.request.method == 'GET':
        if id_ == 1:
            words = instance.sensitive.get_words_1()
        else:
            words = instance.sensitive.get_words_1()
        return '\n'.join(words)
    elif flask.request.method == 'PUT':
        words = flask.request.get_data().decode('utf-8').splitlines()
        if words is None:
            return flask.make_response('error: missing words in json', http.HTTPStatus.BAD_REQUEST)
        if id_ == 1:
            instance.sensitive.add_words_1(words)
        else:
            instance.sensitive.add_words_2(words)
        return ''
    elif flask.request.method == 'DELETE':
        words = flask.request.get_data().decode('utf-8').splitlines()
        if id_ == 1:
            instance.sensitive.remove_words_1(words)
        else:
            instance.sensitive.remove_words_2(words)
        return ''
