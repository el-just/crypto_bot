import Socket from 'socket'

export default class {
    constructor({source=undefined, websocket=undefined}){
        super({source=source})
        this.websocket = websocket;
        this.websocket.onmessage = this.listen}

    async listen(event){
        var message = event.data;
        var action_result;

        if (message){
            message = JSON.parse(message);
            if (message['type'] == 'service' && message['action'])
                action_result = await self.execute(
                        message['action'],
                        message['args'],
                        message['kwargs'],)
                await this.on_data(action_result);
            else:
                await this.push(message);
        }}
