const Stock = require ('./stock')

const
	// запускаем коннект с биржей; коннект включает в себя запись в базу
	stock = new Stock ();

stock.listen ((data)=>{
	console.log (data);
});