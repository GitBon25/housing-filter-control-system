export default class Images {
    config: Record<string, any>
    api: Record<string, any>
    
    constructor(api: Record<string, any>, config: Record<string, any>) {
        this.api = api
        this.config = { ...{
            
        }, ...config }
    }
}