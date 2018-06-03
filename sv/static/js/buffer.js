class Socket {}
class Buffer {
    constructor(name){
        this.name = name;
        if(!this.instances[name]){
            this.instances[name] = new _Buffer(name);}

        this.prototype = this.instances[name].prototype;}}
Buffer.prototype.instances = {}

class _Buffer {
    constructor(name){
        this.name = name;
        this.views = {};
        this.__sockets = new Set([]);}

    connect(socket){
        if (socket === undefined){
            socket = new Socket(this);}
        else {
            socket.source = this;}

        this.__sockets.add(socket);}

    disconnect(socket){
        if (this.__sockets.has(socket){
            this.__sockets.delete(socket);}}

    close(){
        for (socket of this.__sockets){
            socket.close();}}

    add_view(views){
        if (!(views instanceof Array)){
            views = [views];}
        for (view of views){
            this.views[view.name] = view;}}

    async push(source=undefined, data=undefined){
        for (view_name of this.views){
            this.views[view_name].update(data);}

        for (socket of this.__sockets){
            if (socket !== source){
                await socket._data_recieved(data);}}}}
