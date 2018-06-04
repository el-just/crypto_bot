import Socket from './socket.js'

export default class Buffer {
    constructor(name){
        this.name = name;
        if(!this.instances[name]){
            this.instances[name] = new _Buffer(name);}

        this.__proto__ = this.instances[name];}}
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
        if (this.__sockets.has(socket)){
            this.__sockets.delete(socket);}}

    close(){
        for (let socket of this.__sockets){
            socket.close();}}

    add_view(views){
        if (!(views instanceof Array)){
            views = [views];}
        for (let view of views){
            this.views[view.name] = view;}}

    async push({source=undefined, data=undefined}){
        for (let view_name of this.views){
            this.views[view_name].update(data);}

        for (let socket of this.__sockets){
            if (socket !== source){
                await socket._data_recieved(data);}}}}
