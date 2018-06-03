export default class {
    constructor({source=undefined, owner=undefined}){
        this.source = source;
        this.owner = owner;

        if (source){
            source.connect(this);}}

    async push(data){
        await this.source.push({source=this, data=data});}

    close(){
        this.source.disconnect(this);}

    set_owner(owner){
        this.owner = owner;}

    on_data(data){}

    async _data_recieved(data){
        var action_result;
        action_result = await this.__assume_action(data);

        if (action_result){
            await this.push(action_result);}
        else if (data instanceof Object
                && data['type'] === 'service'
                && this.__await_events[data['id']]){
            this.__events_results[data['id']] = data['action_result'];
            this.__await_events[data['id']](data['action_result']);}
        else {
            await this.on_data(data);}}

    async __assume_action(data){
        var response, action, action_result, args;

        try {
            if (this.owner
                    && data['type'] === 'service'
                    && data['action']
                    && data['action'].split('.')[0] === this.owner.name){
                if(this.owner.hasOwnProperty(data['action'].split('.')[1])){
                    action = this.owner[data['action'].split('.')[1]];
                    if (action instanceof Function){
                        args = data['args'];
                        if (Object.keys(data['kwargs']).length > 0){
                            args.append(data['kwargs']);}

                        if (action.constructor.name === 'AsyncFunction'){
                            action_result = await action.apply(
                                    this.owner,
                                    args,);}
                        else {
                            action_result = action(
                                    this.owner,
                                    data['args'],);}}
                    else {
                        action_result = action;}}
                else {
                    throw new Error(`${data['action'].split('.')[0]}`
                        +` has no method ${data['action'].split('.')[1]}`);}}}
        catch(e) {
            action_result = {'error':e.toString()};}
        finally {
            if (action_result !== undefined){
                response = {
                        'type':'service',
                        'id':data['id'],
                        'action_result':action_result,};}}
        return response;}

    async execute(action, args, kwargs){
        var self = this;
        var nonce = new Date().getTime().toString();
        var result;

        await self.push({
            'type':'service',
            'id': nonce,
            'action':action,
            'args':args,
            'kwargs':kwargs,})

        await new Promise((resolve, reject)=>{
            self.__await_events[nonce] = resolve;})

        result = this.__events_results[nonce];

        delete this.__events_results[nonce];
        delete this.__await_events[nonce];

        return result;}}
