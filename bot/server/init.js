//const traider = require ('./traider/traider.js');

//traider.init ();

const s = require ('./poloniex/poloniex.js');
s.getBitterxC().then ((result)=>{console.log (result)})