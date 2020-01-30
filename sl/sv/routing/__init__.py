from routing.handlers.index import Index
from routing.handlers.web_socket import WebSocket
from routing.handlers.favicon import Favicon

routes = [{
    'method' : 'GET',
    'path': '/',
    'handler': Index,
    'name':'index',}, {

    'method' : 'GET',
    'path': '/ws',
    'handler': WebSocket,
    'name':'websocket',}, {

    'method' : 'GET',
    'path': '/favicon.ico',
    'handler': Favicon,
    'name': 'favicon'
    },]
