/*Создадим точку входа*/
document.addEventListener(
  "structureReady",
  function (event) {
    var serverSocket = new ServerSocket ();
    //Свяжем отображение с действиями
    var button = document.querySelector ('button.chartType');
    button.onclick = function () {
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
            'close_bid': {
              x: [1489104000, 1489104900, 1489105800, 1489106700, 1489107600],
              y: [0.00018202, 0.00018368, 0.00018265, 0.00018552, 0.00018258],
              min: 0.00017506,
              max: 0.00039989
            }
          }
        });

      document.body.appendChild (chart.getDOMNode ());

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
