function ServerSocket () {
  var
    path = 'socket/';

  //var socket = new WebSocket("ws://localhost:8081");
  //   socket.send('asd');

  // обработчик входящих сообщений
  // socket.onmessage = function(event) {
  //   document.dispatchEvent(new CustomEvent(
  //     'chart.data.recieved',
  //     { 
  //       detail: {
  //         data: JSON.parse(event.data)
  //       },
  //       bubbles: false,
  //       cancelable: false
  //     }
  //   ));
  // };

  this.send = function (payLoad) {
    return new Promise ((resolve, reject) => {
      var xhr = new XMLHttpRequest();
      xhr.open('POST', path, true);
      xhr.setRequestHeader('Content-Type', 'application/json');

      xhr.onreadystatechange = function() {
        if (xhr.readyState != 4) return;

        if (xhr.status != 200) {
          resolve(false);
        } else {
          resolve(xhr.responseText);
        }
      }

      if (typeof payLoad === 'object') {
        payLoad = JSON.stringify (payLoad);
      }

      xhr.send (payLoad);
    });
  }
}