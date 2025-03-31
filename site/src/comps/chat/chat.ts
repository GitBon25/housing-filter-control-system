import { EventEmmiter } from "../../libs/EventEmmiter"
import { Theme } from "../../libs/Shader"

class Text {
    ui: Theme = new Theme("ChatEstate")
    api: Chat
    config: Record<string, any>
    
    constructor(api: Record<string, any>, config: Record<string, any>) {
        this.config = { ...{
            
        }, ...config }
    }
    
    render(data) {
        
    }
    
    write(data) {
        
    }
    
    send(input) {
        
    }
    
    save(message) {
        
    }
}

class Send {
    ui: Theme = new Theme("ChatEstate")
    api: Chat
    config: Record<string, any>
    
    constructor(api: Record<string, any>, config: Record<string, any>) {
        this.config = { ...{
            
        }, ...config }
    }
}

export default class ChatEstate extends EventEmmiter {
    conf: Record<string, any>
    cont!: HTMLElement 
    tools: Record<string, any> = {}
    input!: HTMLElement
    content!: HTMLElement
    messageInput!: HTMLElement
    
    constructor(config: Record<string, any> = {}) {
        super()
        this.conf = {
            holder: "",
            baseTools: {
                text: Text,
                send: Send,
            },
            tools: {}
            queue: ["text"]
            autoinit: true,
        }
        Object.assign(this.conf, config)
        Object.assign(this.conf.tools, this.conf.baseTools)
        
        if (this.conf.holder instanceof HTMLElement) {
            this.cont = this.conf.holder
        } else {
            const node = document.querySelector(this.conf.holder)
            if (!node) throw new Error("Нет могу найти элемент")
            this.cont = node
        }
        
        if (this.conf.autoinit) this.init()
    }
    
    init() {
        this.initTools()
        this.initChat()
    }
    
    initTools() {
        for (const key in this.conf.tools) {
            let res = this.conf.tools[key]
            
            if (typeof res !== "function") {
                res = {
                    plugin: res
                }
            }
            
            const plugin = new res.plugin(this, res)
            this.tools[key] = plugin
        }
    }
    
    initChat() {
        this.initDesign()
        this.initCore()
        this.initContent()
        this.initInput()
    }
    
    initDesign() {
        const ui = this.ui
        
        ui.add(".chest", {
            
        })
        
        ui.add(".chest-content-box", {
            
        })
        
        ui.add(".chest-content", {
            
        })
        
        ui.add(".chest-input-box", {
            
        })
        
        ui.add(".chest-input", {
            
        })
        
        ui.add(".chest-input-content", {
            
        })
        
        ui.add(".chest-input-message", {
            
        })
        
        ui.add(".chest-input-menu", {
            
        })
        
        ui.add(".chest-input-menu-btnsBox", {
            
        })
        
        ui.add(".chest-input-menu-ctrlBox")
        
        
        
        ui.add(".chest-message-box", {
            
        })
        
        ui.add(".chest-message", {
            
        })
        
        ui.add(".chest-message-content", {
            
        })
        
        
        ui.add(".chest-input-menu-btn", {
            
            "&-icon": {
                
            },
            
            "&-name": {
                
            },
        })
    }
    
    initCore() {
        this.cont.classList.add("chest")
        
        this.on("newMessage", {
            let elements = Array.from(this.content.children)
            
            let fragment = document.createDocumentFragment();
            
            elements.sort((a, b) => parseInt(a.getAttribute("data-chest-id")) - parseInt(b.getAttribute("data-chest-id")))
            
            elements.forEach(element => {
              fragment.appendChild(element)
            })
            
            container.appendChild(fragment)
        })
        
        this.on("destroy", () => {
            this.cont.remove()
            this.ui.delete()
        })
        
        this.on("send", (e) => {
            // ищешь кнопку отправки и если она забоокирована - вызыааешь prevent()
        })
    }
    
    initContent() {
        const box = document.createElement("div")
        box.classList.add("chest-content-box")
        this.content = box
        
        const content = document.createElement("div") 
        content.classList.add("chest-content")
        
        this.cont.appendChild(box)
    }
    
    initInput() {
        const inpBox = document.createElement("div")
        inpBox.classList.add("chest-input-box")
        this.input = inpBox
        this.cont.appendChild(this.input)
        
        const input = document.createElement("div")
        input.classList.add("chest-input")
        inpBox.appendChild(input)
        
        const content = document.createElement("div")
        content.classList.add("chest-input-content")
        input.appendChild(content)
        
        const messageInp = document.createElement("div")
        messageInp.classList.add("chest-input-message")
        content.appendChild(messageInp)
        
        const menu = document.createElement("div")
        menu.classList.add("chest-input-menu")
        content.appendChild(menu)
        
        this.initMenu(menu)
    }
    
    initMenu(menu) {
        const ctrl = []
        const btns = []
        
        for (const tool of this.tools) {
            const { name, icon, type } = tool.config
            if (!name && !icon) continue
            
            const btn = document.createElement("button")
            btn.classList.add("chest-input-menu-btn")
            
            const icoBox = document.createElement(div)
            iconBox.classList.add("chest-input-menu-btn-icon")
            if (icon) {
                iconBox.innerHtml = icon
                btn.appendChild(iconBox)
            }
            
            const nameBox = document.createElement("div")
            nameBox.classList.add("chest-input-menu-btn-name")
            const span = document.createElement("div")
            nameBox.appendChild(span)
            if (name) {
                span.innerHtml = name
                btn.appendChild(nameBox)
            }
            
            if (type === "ctrl") {
                ctrl.push(btn)
            } else {
                btns.push(btn)
            }
        }
        
        const btnsBox = document.createElement("div")
        btnsBox.classList.add("chest-input-menu-btnsBox")
        btns.forEach((btn) => btnsBox.appendChild(btn))
        menu.appendChild(btnsBox)
        
        const ctrlBox = document.createElement("div")
        ctrlBox.classList.add("chest-input-menu-ctrlBox")
        ctrl.forEach((btn) => ctrlBox.appendChild(btn))
        menu.appendChild(ctrlBox)
    }
    
    initData(data: Record<string, any>) {
        if (data.input) {
            const toolData = data.input.messages
            for (const toolName in toolData) {
                const tool = this.tools[toolName]
                if (!tool) return
                
                if (typeof tool.write !== "function") return
                const rend = tool.write(toolData[toolName])
                if (!(rend instanceof HTMLElement)) return
                
                const inpContent = this.input.querySelector(".chest-input-content")
                inpContent.appendChild(rend)
            }
        }
        if (data.messages) {
            for (const message of data.messages) {
                this.message(data)
            }
        }
    }
    
    message(msData: Record<string, any>) {
        let { data, side, id } = msData
        
        if (id === undefined) {
            let lastMs = this.content.lastElelemntChild
            if (lastMs) {
                id = Number(lastMs.getAttribute("data-chest-id") || "0") + 1
            } else {
                id = 0
            }
        }
        
        const box = document.createElement("div")
        box.classList.add("chest-message-box")
        box.setAttribute("data-chest-direction", side || "right")
        box.setAttribute("data-chest-id", id)
        
        const message = document.createElement("div")
        message.classList.add("chest-message")
        
        const content = document.createElement("div")
        content.classList.add("chest-message-content")
        
        for (const toolName in data) {
            const tool = this.tools[toolName]
            let msData = data[toolName]
            
            const toolBox = document.createElement("div")
            toolBox.classList.add("chest-message-toolBox")
            
            if (typeof tool.render !== "function") continue
            const rend = tool.render(msData, toolBox)
            if (!(rend instanceof HTMLElement)) continue
            
            toolBox.appendChild(rend)
            toolBox.setAttribute("data-chest-tool", toolName)
            content.appendChild(toolBox)
        }
    
        this.content.appendChild(box)
        this.emit("newMessage", { message: box, id: id, side: side, data: data})
        this.emit("change", { type: "newMessage" })
    }
    
    inputData() {
        const data = {
            data: {},
            side: "right"
        }
        
        const content = this.input.querySelector(".chest-message-content")
        content.children.forEach((box) => {
            const toolName = box.getAttribute("data-chest-tool")
            if (!toolName) return 
            const tool = this.tools[toolName]
            if (!tool) return
            if (typeof tool.send !== "function") return
            let data = tool.send(box)
            if (!data) return
            
            data.data[toolName] = data
        })
        
        this.message(data)
    }
    
    clearInput() {
        this.emit("clearInput")
        
        let content = this.input.querySelector(".chest-message-content")
        if (content) content.innerHtml = ""
    }
    
    send(data = this.inputData()) {
        const e = this.emit("send", { data: data })
        if (e.prevented) return
        this.clearInput()
        this.message(data)
    }
    
    save() {
        let data = {
            input: this.inputData(),
            messages: [],
        }
        
        this.content.children.forEach((box) => {
            let msData = {
                id: Number(box.getAttribute("data-chest-id") as string),
                side: box.getAttribute("data-chest-direction") || "right"
                data: {}
            }
            
            const content = this.box.querySelector(".chest-message-content")
            content.children.forEach((toolBox) => {
                const toolName = toolBox.getAttribute("data-chest-tool")
                if (!toolName) return
                const tool = this.tools[toolName]
                if (!tool) return
                if (typeof tool.save !== "function") return
                const data = tool.save(toolBox)
                if (!data) return
                
                msData.data[toolName] = data
            })
            
            data.messages.push(msData)
        })
        
        return data
    }
}

//data
{
    input: {
        message: {},
    },
    messages: 
    [
        {
            id: 123,
            side: "left"
            data: {
                "text": {
                    text: "бла бла"
                }
            }
        },
    ]
}