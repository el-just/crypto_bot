function R () {
  function _Number (data) {
    var
      pow,
      value;

    function _getValue () {
      return value;
    }

    function _getPow () {
      return pow;
    }

    function _setValue (data) {
      if (typeof data === 'object') {
        value = data.value;
        pow = data.pow;
      }
      else {
        pow = (data+'').split ('.')[1] ? (data+'').split ('.')[1].length : 0;
        value = (data | 0)*Math.pow(10, pow)+parseInt((data+'').split ('.')[1] ? (data+'').split ('.')[1] : 0, 10);
      }
    }

    function _toPrecision (powTo) {
      if (powTo > pow) {
        value = value*Math.pow (10, powTo - pow);
        pow = powTo;
      }
    }

    function _getReal () {
      var
        integers = Math.abs((value / Math.pow (10, pow)) | 0),
        floats = Math.abs((value % Math.pow (10, pow))) + '';

        while (pow-floats.length > 0) {
          floats = '0'+floats;
        }

      return parseFloat ((value < 0 ? '-' : '')+integers+'.'+floats);
    }

    this.getValue = _getValue;
    this.getPow = _getPow;
    this.setValue = _setValue;
    this.toPrecision = _toPrecision;
    this.getReal = _getReal;

    _setValue (data);
  }

  function _residual (reduced, subtracted) {
    var
      overallPow = reduced.getPow() > subtracted.getPow () ? reduced.getPow() : subtracted.getPow ();
    
    reduced.toPrecision (overallPow);
    subtracted.toPrecision (overallPow);

    return new _Number ({
      pow: overallPow,
      value: reduced.getValue() - subtracted.getValue ()
    });
  }

  this.Number = _Number;
  this.residual = _residual;
}

Math.R = new R();