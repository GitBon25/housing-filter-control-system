import ChatEstate from "../comps/chat/chat"
import Images from "../comps/chat/plugins/images"
import { Theme } from "../libs/Shader"

export default class {
    router: Record<string, any>
    chat!: ChatEstate
    chatBox!: HTMLElement
    ui: Theme = new Theme("ChatPage")
    
    constructor(router: Record<string, any>) {
        this.router = router
        this.initUI()
    }
    
    initUI() {
        const ui = this.ui
        console.log(ui)
        ui.add(".chat-box", {
            width: "100%",
            height: "auto",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
        })
    }
    
    init() {
        const main = document.querySelector("main")
        const chatBox = document.createElement("div")
        this.chatBox = chatBox
        chatBox.classList.add("chat-box")
        main.appendChild(chatBox)
        
        const chat = document.createElement("div")
        chatBox.appendChild(chat)
        
        this.chat = new ChatEstate({
            holder: chat,
            tools: {
                image: {
                    name: undefined,
                    icon: undefined,
                    plugin: Images,
                }
            },
        })
    }
    
    exit() {
        this.chat.emit("destroy")
        this.chatBox.remove()
        const main = document.querySelector("main")
        if (main) main.innerHtml = ""
    }
}