import Buffer from './buffer.js'
window._ = {};
function request_action(event) {
        var action = document.forms.action_requestor.elements.action.value;
        window._.websocket.send(action);

        return false;}

window._.websocket = new WebSocket(
        'ws://'+window.location.host+'/ws');

window._.websocket.onmessage = function(event) {
    document.dispatchEvent(new CustomEvent(
            'socket.data.recieved', {
                detail: {
                    data: event.data
                },
                bubbles: false,
                cancelable: false,}));};

document.addEventListener("socket.data.recieved",
        function(event) {
            console.log (
                'socket.data.recieved: ' + event.detail.data);},
        false,);

document.querySelector('div.settings_button').addEventListener(
    'click', function(event) {
        document.querySelector(
            'div.settings_container').classList.toggle(
                'settings_visible')});
