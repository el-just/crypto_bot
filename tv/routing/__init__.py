from routing.handlers.login import Login
from routing.handlers.web_socket import WebSocket

routes = [{
    'method' : 'GET',
    'path': '/',
    'handler': Login,
    'name':'login'
    }, {
    'method' : 'GET',
    'path': '/ws',
    'handler': WebSocket,
    'name':'websocket'
    }]
