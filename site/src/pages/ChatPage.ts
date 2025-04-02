import ChatEstate from "../comps/chat/chat"
import Images from "../comps/chat/plugins/images"
import Placeholder from "../comps/chat/plugins/placeholder"
import { Theme } from "../libs/Shader"
import { req } from "../libs/Req"

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
            height: "100%",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            justifyContent: "center",
        })
    }
    
    init() {
        const main = document.querySelector("main") as HTMLElement
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
                },
                placeholder: {
                    plugin: Placeholder,
                }
            },
        })

        let send = false
        this.chat.on("newMessage", async (e: Record<string, any>) => {
            const { data, side } = e
            const text = data.text?.text
            if (side !== 'right' || !text) return
            if (send) {
                e.prevent()
                return
            }
            send = true
            
            
            const res = await req("/task", {
                method: "POST",
                body: JSON.stringify({
                    text: text
                })
            })
            
            const sms = await this.poll(res)
            console.log(sms)
            setTimeout(() => {
                send = false
                this.chat.message({
                    side: "left",
                    data: {
                        text: {
                            text: "Губу закатай"
                        }
                    }
                })
            }, 3000)
        })
        
        this.chat.initData({
            input: {
                message: {
                    text: {
                        text: "Найди мне квартиру в москве за 60000 рублей "
                    }
                }
            }
        })
    }

    async poll(res: Record<string, any>) {
        const checkData = async () => {
            try {
                const data = await req(`/task/${res.id}`, {
                    "method": "GET"
                })
                
                if (data.status === 'done') {
                    return data
                } else {
                    setTimeout(checkData, 1000);
                }
            } catch (error) {
                console.log(error)
            }
        }
        
        return checkData()
    }
    
    exit() {
        this.chat.emit("destroy")
        this.chatBox.remove()
        const main = document.querySelector("main")
        if (main) main.innerHTML = ""
        this.ui.delete()
    }

    infoUI() {
        this.ui.add(".chest-infoBox", {
            width: "80%",
            display: 'flex',
            alignItems: "center",
            flexDirection: "column",
        })
    }
}