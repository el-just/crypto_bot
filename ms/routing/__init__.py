from routing.handlers.index import Index

routes = [{
	'method' : 'GET',
	'path': '/',
	'handler': Index,
	'name':'root'
	}]