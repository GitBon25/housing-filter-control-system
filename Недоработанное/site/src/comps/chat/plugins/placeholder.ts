export default class Placeholder {
    config: Record<string, any>
    api: Record<string, any>
    content!: HTMLElement
    toolName: string = ""
    
    constructor(api: Record<string, any>, config: Record<string, any>) {
        this.api = api
        this.config = { ...{
            data: {}
        }, ...config }

        this.api.ui.add(".chest-placeholder-box", {
            width: "100%",
            height: "auto",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            flexDirection: "column",
        })

        this.api.on("newMessage", () => {
            //this.content?.remove()
        })

        this.api.on("initData", (e: Record<string, any>) => {
            if (!e.data.messages || !e.data.messages.length) return
            this.content?.remove()
        })

        this.api.on("ready", () => {
            for (let tool in this.api.tools) {
                if (this.api.tools[tool] === this) {
                    this.toolName = tool
                    break
                }
            }
            this.init()
        })
    }

    init() {
        this.api.message({
            data: {
                [this.toolName]: this.config.data,
            },
            side: "center",
        })
    }

    render(data: Record<string, any>) {
        data = { ...{

        }, ...data}
        const box = document.createElement("div")
        box.classList.add("chest-placeholder-box")
        box.innerHTML = `<h1>Бот для поиска жилья</h1>`
        return box
    }
}