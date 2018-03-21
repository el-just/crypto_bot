/*
function send (payLoad) {
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
*/

document.addEventListener(
   'structureReady',
   function (event) {
      var socket = new WebSocket('ws://'+window.location.host+'/ws');
      
      socket.onmessage = function(event) {
         document.dispatchEvent(new CustomEvent(
            'socket.data.recieved',
            { 
               detail: {
                  data: event.data
               },
               bubbles: false,
               cancelable: false
            }
         ));
      };

      document.addEventListener(
         "socket.data.recieved",
         function (event) {
            console.log ('socket.data.recieved: ' + event.detail.data);
         },
         false
      );

     window.w_s = socket; 
   },
   false
);
