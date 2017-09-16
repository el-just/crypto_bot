/*Создадим точку входа*/
document.addEventListener(
  "structureReady",
  function (event) {
    var serverSocket = new ServerSocket ();
    //Свяжем отображение с действиями
    var button = document.querySelector ('button.chartType');
    button.onclick = function () {

      serverSocket.send ('asd').then ((data)=>{
        var
        chart = new Chart ({
          canvas: {
            width: 1100,
            height: 300
          },
          axises: {
            x: {
              padding: 40
            },
            y: {
              padding: 40
            }
          },
          scale: 1,
          data: {
            'close': {
              x: data.reduce ((result, item, idx, items)=>{
                return result.push (item.date);
              }, []),
              y: data.reduce ((result, item, idx, items)=>{
                return result.push (item.close);
              }, []),
              min: 0.00017506,
              max: 0.00039989
            }
          }
        });

        document.body.appendChild (chart.getDOMNode ());
      });

      document.addEventListener(
        "chart.data.recieved",
        function (event) {
          chart.updateChart ('close', event.detail.data);
        },
        false
      );
    }
  },
  false
);

// children – только дочерние узлы-элементы, то есть соответствующие тегам.
// firstElementChild, lastElementChild – соответственно, первый и последний дети-элементы.
// previousElementSibling, nextElementSibling – соседи-элементы.
// parentElement – родитель-элемент.
