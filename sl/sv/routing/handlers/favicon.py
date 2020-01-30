from aiohttp import web

def Favicon (request):
    return web.FileResponse('static/favicon.ico')
