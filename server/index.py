import http

import flask

from app import instance
from server import app


@app.route('/api/ping')
def handle_api():
    return 'hello fkxxyz!'


@app.route('/api/test', methods=['PUT'])
def handle_test():
    # 从 body 中读取文本
    text = flask.request.get_data(as_text=True)

    try:
        instance.admin.master_test(text)
    except Exception as e:
        return flask.make_response(str(e), http.HTTPStatus.INTERNAL_SERVER_ERROR)

    return flask.make_response("", http.HTTPStatus.OK)
