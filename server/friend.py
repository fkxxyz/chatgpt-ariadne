import http

import flask

from admin import error
from app import instance
from server import app


@app.route('/api/friend/create', methods=['PUT'])
def handle_friend_create():
    user_id = flask.request.args.get('user_id')
    if user_id is None or len(user_id) == 0:
        return flask.make_response('error: missing user_id query', http.HTTPStatus.BAD_REQUEST)
    try:
        user_id = int(user_id)
    except ValueError:
        return flask.make_response('error: user_id must be int', http.HTTPStatus.BAD_REQUEST)
    data = flask.request.get_json()
    comment = data.get('comment', "")
    source = data.get('source', "")

    try:
        reply = instance.admin.session_friend_create(user_id, comment, source)
    except error.AdminError as e:
        return flask.make_response(str(e), e.HttpStatus)
    except Exception as e:
        return flask.make_response(str(e), http.HTTPStatus.INTERNAL_SERVER_ERROR)

    return flask.make_response(reply, http.HTTPStatus.OK)


@app.route('/api/friend/inherit', methods=['PUT'])
def handle_friend_inherit():
    user_id = flask.request.args.get('user_id')
    if user_id is None or len(user_id) == 0:
        return flask.make_response('error: missing user_id query', http.HTTPStatus.BAD_REQUEST)
    try:
        user_id = int(user_id)
    except ValueError:
        return flask.make_response('error: user_id must be int', http.HTTPStatus.BAD_REQUEST)
    data = flask.request.get_json()
    memo = data.get('memo')
    if memo is None or len(memo) == 0:
        return flask.make_response('error: missing memo in json', http.HTTPStatus.BAD_REQUEST)
    history = data.get('history')
    if history is None or len(history) == 0:
        return flask.make_response('error: missing history in json', http.HTTPStatus.BAD_REQUEST)

    try:
        instance.admin.session_friend_inherit(user_id, memo, history)
    except error.AdminError as e:
        return flask.make_response(str(e), e.HttpStatus)
    except Exception as e:
        return flask.make_response(str(e), http.HTTPStatus.INTERNAL_SERVER_ERROR)

    return flask.make_response("", http.HTTPStatus.OK)


@app.route('/api/friend/send', methods=['POST'])
def handle_friend_send():
    user_id = flask.request.args.get('user_id')
    if user_id is None or len(user_id) == 0:
        return flask.make_response('error: missing user_id query', http.HTTPStatus.BAD_REQUEST)
    try:
        user_id = int(user_id)
    except ValueError:
        return flask.make_response('error: user_id must be int', http.HTTPStatus.BAD_REQUEST)
    data = flask.request.get_json()
    message = data.get('message')
    if message is None or len(message) == 0:
        return flask.make_response('error: missing message in json', http.HTTPStatus.BAD_REQUEST)

    try:
        reply = instance.admin.session_friend_send(user_id, message)
    except error.AdminError as e:
        return flask.make_response(str(e), e.HttpStatus)
    except Exception as e:
        return flask.make_response(str(e), http.HTTPStatus.INTERNAL_SERVER_ERROR)

    return flask.make_response(reply, http.HTTPStatus.OK)
