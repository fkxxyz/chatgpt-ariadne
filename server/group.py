import http

import flask

from admin import error
from app import instance
from common import group_chati_session_id
from server import app


@app.route('/api/group/create', methods=['PUT'])
def handle_group_create():
    group_id = flask.request.args.get('group_id')
    if group_id is None or len(group_id) == 0:
        return flask.make_response('error: missing group_id query', http.HTTPStatus.BAD_REQUEST)
    try:
        group_id = int(group_id)
    except ValueError:
        return flask.make_response('error: group_id must be int', http.HTTPStatus.BAD_REQUEST)

    try:
        reply = instance.admin.session_group_create(group_id)
    except error.AdminError as e:
        return flask.make_response(str(e), e.HttpStatus)
    except Exception as e:
        return flask.make_response(str(e), http.HTTPStatus.INTERNAL_SERVER_ERROR)

    return flask.make_response(reply, http.HTTPStatus.OK)


@app.route('/api/group/inherit', methods=['PUT'])
def handle_group_inherit():
    group_id = flask.request.args.get('group_id')
    if group_id is None or len(group_id) == 0:
        return flask.make_response('error: missing group_id query', http.HTTPStatus.BAD_REQUEST)
    try:
        group_id = int(group_id)
    except ValueError:
        return flask.make_response('error: group_id must be int', http.HTTPStatus.BAD_REQUEST)
    data = flask.request.get_json()
    memo = data.get('memo')
    if memo is None or len(memo) == 0:
        return flask.make_response('error: missing memo in json', http.HTTPStatus.BAD_REQUEST)
    history = data.get('history')
    if history is None or len(history) == 0:
        return flask.make_response('error: missing history in json', http.HTTPStatus.BAD_REQUEST)

    try:
        instance.admin.session_group_inherit(group_id, memo, history)
    except error.AdminError as e:
        return flask.make_response(str(e), e.HttpStatus)
    except Exception as e:
        return flask.make_response(str(e), http.HTTPStatus.INTERNAL_SERVER_ERROR)

    return flask.make_response("", http.HTTPStatus.OK)


@app.route('/api/group/send', methods=['POST'])
def handle_group_send():
    group_id = flask.request.args.get('group_id')
    if group_id is None or len(group_id) == 0:
        return flask.make_response('error: missing group_id query', http.HTTPStatus.BAD_REQUEST)
    try:
        group_id = int(group_id)
    except ValueError:
        return flask.make_response('error: group_id must be int', http.HTTPStatus.BAD_REQUEST)
    data = flask.request.get_json()
    message = data.get('message')
    if message is None or len(message) == 0:
        return flask.make_response('error: missing message in json', http.HTTPStatus.BAD_REQUEST)

    try:
        reply = instance.admin.session_group_send(group_id, message)
    except error.AdminError as e:
        return flask.make_response(str(e), e.HttpStatus)
    except Exception as e:
        return flask.make_response(str(e), http.HTTPStatus.INTERNAL_SERVER_ERROR)

    return flask.make_response(reply, http.HTTPStatus.OK)


@app.route('/api/group/welcome', methods=['PUT'])
def handle_group_welcome():
    group_id = flask.request.args.get('group_id')
    if group_id is None or len(group_id) == 0:
        return flask.make_response('error: missing group_id query', http.HTTPStatus.BAD_REQUEST)
    try:
        group_id = int(group_id)
    except ValueError:
        return flask.make_response('error: group_id must be int', http.HTTPStatus.BAD_REQUEST)
    data = flask.request.get_json()
    prompt = data.get('prompt')
    if prompt is None or len(prompt) == 0:
        return flask.make_response('error: missing prompt in json', http.HTTPStatus.BAD_REQUEST)

    try:
        instance.admin.on_group_welcome_prompt(group_id, prompt)
    except error.AdminError as e:
        return flask.make_response(str(e), e.HttpStatus)
    except Exception as e:
        return flask.make_response(str(e), http.HTTPStatus.INTERNAL_SERVER_ERROR)

    return ""
