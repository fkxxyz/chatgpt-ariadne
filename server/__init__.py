import flask

app = flask.Flask(__name__)

from server.index import *
from server.friend import *
from server.group import *
from server.sensitive import *
