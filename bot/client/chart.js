function Chart (config) {
  var
    _SVG_NAME_SPACE = 'http://www.w3.org/2000/svg',
    _DOM = {
      axises: {},
      charts: {}
    },
    _CONFIG = config;
  
  function _getDOMNode () {
    return _DOM.main;
  }

  function _drawLine (x1, y1, x2, y2) {
    var
      line = document.createElementNS(_SVG_NAME_SPACE, 'line');

    line.setAttribute ('x1', x1);
    line.setAttribute ('y1', y1);
    line.setAttribute ('x2', x2);
    line.setAttribute ('y2', y2);
    line.setAttribute ('stroke-width', '1');
    line.setAttribute ('stroke', '#CCC');

    _DOM.main.append (line);

    return line;
  }

  function _drawPolyline (points) {
    var
      polyline = document.createElementNS(_SVG_NAME_SPACE, 'polyline');

    polyline.setAttribute ('stroke-width', '1');
    polyline.setAttribute ('stroke', '#0074d9');
    polyline.setAttribute ('fill', 'none');
    polyline.setAttribute ('points', points);

    _DOM.main.append (polyline);

    return polyline;
  };

  function _resolvePoint (name, ) {

  }

  function _addChart (name, data) {
    var
      min = new Math.R.Number (data.min),
      max = new Math.R.Number (data.max),
      resMaxMin = Math.R.residual (max, min),

      stepWeight = (
        resMaxMin.getValue()
        /
        ((((_CONFIG.canvas.height - _CONFIG.axises.y.padding) / _CONFIG.scale) | 0) - 2)
      ) | 0,

      points = '';

    for (let pointID = 0; pointID < data.x.length; pointID++) {
      //var point = _resolvePoint ();

      var
        x = _CONFIG.axises.x.padding + pointID*_CONFIG.scale,
        yR = new Math.R.Number(data.y[pointID]),
        y = _CONFIG.canvas.height - (
          (((Math.R.residual (yR, min).getValue() / stepWeight) + 1) | 0)*_CONFIG.scale
          +
          Math.floor((Math.R.residual (yR, min).getValue() % stepWeight) * _CONFIG.scale / stepWeight) + _CONFIG.axises.y.padding
        );

      if (points.length) {
        points += ' '
      }
      points += x + ',' + y;
    }

    _DOM.charts[name] = _drawPolyline (points);
  }

  function _updateChart (name, data) {
    console.log (data);
    _DOM.charts[name].getAttribute ('points');
  }

  function _init () {
    _DOM.main = document.createElementNS(_SVG_NAME_SPACE, 'svg');
    _DOM.main.setAttribute ('width', _CONFIG.canvas.width);
    _DOM.main.setAttribute ('height', _CONFIG.canvas.height);
    _DOM.main.setAttribute ('viewBox', '0 0 '+_CONFIG.canvas.width+' '+_CONFIG.canvas.height);
    _DOM.main.setAttribute ('class', 'chart');

    _DOM.axises.x = _drawLine (
      0,                                                //x1
      _CONFIG.canvas.height - _CONFIG.axises.x.padding, //y2
      _CONFIG.canvas.width,                             //x2
      _CONFIG.canvas.height - _CONFIG.axises.x.padding  //y2
    );
    _DOM.axises.y = _drawLine (
      _CONFIG.canvas.width - _CONFIG.axises.x.padding,  //x1
      0,                                                //y2
      _CONFIG.canvas.width - _CONFIG.axises.y.padding,  //x2
      _CONFIG.canvas.height                             //y2
    );

    for (let name of Object.keys(_CONFIG.data)) {
      _addChart (name, _CONFIG.data[name]);
    }
  }

  this.getDOMNode = _getDOMNode;
  this.addChart = _addChart;
  this.updateChart = _updateChart;

  _init ();
}