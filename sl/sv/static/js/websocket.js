import Socket from './socket.js'

export default class extends Socket {
    constructor({source=undefined, websocket=undefined}){
        super({source:source});
        this.__websocket = websocket;
        this.__websocket.onmessage = this.listen;}

    async listen(event){
        var message = event.data;
        var action_result;

        if (message){
            message = JSON.parse(message);
            if (message['type'] == 'service' && message['action']){
                action_result = await self.execute(
                        message['action'],
                        message['args'],
                        message['kwargs'],);
                await this.on_data(action_result);}
            else {
                await this.push(message);}}}
    
    async on_data(data){
        data = JSON.stringify(data);
        await this.__websocket.send(data);}}
