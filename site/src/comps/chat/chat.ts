import { AppEvent, EventEmmiter } from "../../libs/EventEmmiter"
import { Theme } from "../../libs/Shader"

class Text {
    ui: Theme
    api: ChatEstate
    config: Record<string, any>
    
    constructor(api: ChatEstate, config: Record<string, any>) {
        this.api = api
        this.config = { ...{
            placeholder: "Хочу вартиру в москве бесплатно"
        }, ...config }
        this.ui = api.ui
        this.initUI()
    }

    initUI() {
        const ui = this.ui

        ui.add(".chest-text-box", {
            width: "100%",
            height: "auto",
            padding: "3px",
            display: "flex",
            alignItems: "center",
        })

        ui.add(".chest-text", {
            all: "unset",
            width: '100%',
            display: "block",
            wordWrap: "break-word",
            whiteSpace: "pre-wrap",
            fontSize: "110%",
        })
        ui.add(".chest-placeholder:empty:not([data-chest-has-content])::before", {
            content: "attr(data-chest-placeholder)",
            pointerEvents: "none",
            color: "rgb(var(--placeholder))",
        })

        this.api.cont.addEventListener("input", (e) => {
            const inp = e.target as HTMLElement
            if ((inp.innerHTML === "<br>" || inp.innerHTML === '\n') && inp.hasAttribute("data-chest-trimInp")) {
                inp.innerHTML = ""
            }

            if (inp.classList.contains("chest-placeholder")) {
                if (inp.innerText === "") {
                    inp.removeAttribute("data-chest-has-content")
                } else {
                    inp.setAttribute("data-chest-has-content", "")
                }
            }
        })
    }
    
    render(data: Record<string, any>) {
        data = { ...{
            text: ""
        }, ...data }
        const inpBox = document.createElement("div")
        inpBox.classList.add("chest-text-box")

        const cont = document.createElement("div")
        cont.classList.add("chest-text")
        cont.textContent = data.text
        inpBox.appendChild(cont)

        return inpBox
    }
    
    write(data: Record<string, any>) {
        data = { ...{
            text: ""
        }, ...data}

        const inpBox = document.createElement("div")
        inpBox.classList.add("chest-text-box")

        const inp = document.createElement("div")
        inp.setAttribute("contenteditable", "true")
        inp.setAttribute('data-chest-placeholder', this.config.placeholder)
        inp.setAttribute("data-chest-trimInp", "")
        inp.classList.add("chest-text", "chest-placeholder")
        inp.textContent = data.text
        inpBox.appendChild(inp)

        return inpBox
    }
    
    send(input: HTMLElement) {
        const inp = input.querySelector(".chest-text")
        return {
            text: inp?.textContent || ""
        }
    }
    
    save(message: HTMLElement) {
        const inp = message.querySelector(".chest-text")
        return {
            text: inp?.textContent || ""
        }
    }
}

class Send {
    api: ChatEstate
    config: Record<string, any>
    
    constructor(api: ChatEstate, config: Record<string, any>) {
        this.config = { ...{
            icon: '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><path d="M12,24A12,12,0,1,0,0,12,12.013,12.013,0,0,0,12,24ZM6.293,9.465,9.879,5.879h0a3,3,0,0,1,4.243,0l3.585,3.586.024.025a1,1,0,1,1-1.438,1.389L13,7.586,13.007,18a1,1,0,0,1-2,0L11,7.587,7.707,10.879A1,1,0,1,1,6.293,9.465Z"/></svg>',
            type: "ctrl"
        }, ...config }
        this.api = api
        
        this.init()
    }

    init() {
        this.api.cont.addEventListener("keydown", (e) => {
            if (e.shiftKey || e.ctrlKey) return
            if (e.code === "Enter") {
                this.api.send()
            }
        })
    }

    attachBtn(btn: HTMLElement) {
        btn.addEventListener("click", () => {
            this.api.send()
        })
    }
}

export default class ChatEstate extends EventEmmiter {
    conf: Record<string, any>
    cont!: HTMLElement 
    tools: Record<string, any> = {}
    input!: HTMLElement
    content!: HTMLElement
    messageInput!: HTMLElement
    ui: Theme = new Theme("ChatUI")
    
    constructor(config: Record<string, any> = {}) {
        super()
        this.conf = {
            holder: "",
            baseTools: {
                text: Text,
                send: Send,
            },
            tools: {},
            queue: 
            [
                "image",
                "text"
            ],
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
            
            if (typeof res === "function") {
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
        console.log(ui)
        ui.add(".chest", {
            width: "100%",
            height: "auto",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            border: "1px solid white",
        })
        
        ui.add(".chest-content-box", {
            width: "100%",
            display: "flex",
            alignItems: "center",
            flexDirection: "column",
            height: "auto",
            padding: "5px",
        })
        
        ui.add(".chest-content", {
            width: "90%",
            height: "auto",
            maxHeight: "100%",
            
        })
        
        ui.add(".chest-input-box", {
            width: "100%",
            height: "auto",
            padding: "5px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
        })
        
        ui.add(".chest-input", {
            width: "90%",
            height: "90%",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
        })
        
        ui.add(".chest-input-content", {
            borderRadius: "12px",
            backgroundColor: "rgba(var(--bg-nd), 0.8)",
            width: "100%",
            height: "auto",
            padding: "5px",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            gap: "5px",
        })
        
        ui.add(".chest-input-message", {
            width: "100%",
            display: "flex",
            flexDirection: "column",
            gap: "5px",
            alignItems: "center",
            height: "auto",
        })
        
        ui.add(".chest-input-menu", {
            width: "100%",
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
        })
        
        ui.add(".chest-input-menu-btnsBox", {
            width: "100%",
            display: "flex",
            alignItems: 'center',
            flexDirection: "row",
        })
        
        ui.add(".chest-input-menu-ctrlBox", {
            width: "100%",
            display: "flex",
            alignItems: 'center',
            flexDirection: "row",
            justifyContent: "flex-end"
        })
        
        
        
        ui.add(".chest-message-box", {
            width: "100%",
            padding: "8px",
            display: "flex",
            flexDirection: "row",
        })
        
        ui.add(".chest-message", {
            width: "35%",
            height: "auto",
            borderRadius: "8px",
            backgroundColor: "rgba(var(--bg-nd), 0.8)",
            padding: "5px",
            display: "flex",
            flexDirection: "row",
            alignItems: "center",
        })
        
        ui.add(".chest-message-content", {
            width: "100%",
            display: "flex",
            flexDirection: "column",
            alignItems: "center",
            height: "auto",
            gap: "5px",
        })
        
        
        ui.add(".chest-input-menu-btn", {
            borderRadius: "8px",
            width: "auto",
            display: "flex",
            flexDirection: "row",
            padding: "3px",
            gap: "8px",
            cursor: "pointer",
            border: "rgb(var(--border))",
            transition: "transform 0.3s",

            "&:active": {
                transform: "scale(1.1)"
            },
            
            "&-icon": {
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: "auto",
                height: "auto",
                
                "svg": {
                    width: "25px",
                    height: "25px",
                    fill: "rgb(var(--color))",
                    aspectRatio: "1/1",
                }
            },
            
            "&-name": {
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                width: "auto",
                height: "auto",
            },
        })
    }
    
    initCore() {
        this.cont.classList.add("chest")
        
        this.on("newMessage", () => {
            let elements = Array.from(this.content.children)
            
            let fragment = document.createDocumentFragment();
            
            elements.sort((a, b) => parseInt(a.getAttribute("data-chest-id") as string) - parseInt(b.getAttribute("data-chest-id") as string))
            
            elements.forEach(element => {
              fragment.appendChild(element)
            })
            
            this.content.appendChild(fragment)
        })
        
        this.on("destroy", () => {
            this.cont.remove()
            this.ui.delete()
        })
        
        this.on("send", (e: AppEvent) => {
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
    
    initMenu(menu: HTMLElement) {
        const ctrl = []
        const btns = []
        
        for (const toolName in this.tools) {
            const tool = this.tools[toolName]
            const { name, icon, type } = tool.config
            if (!name && !icon) continue
            
            const btn = document.createElement("button")
            btn.classList.add("chest-input-menu-btn")
            
            const iconBox = document.createElement("div")
            iconBox.classList.add("chest-input-menu-btn-icon")
            if (icon) {
                iconBox.innerHTML = icon
                btn.appendChild(iconBox)
            }
            
            const nameBox = document.createElement("div")
            nameBox.classList.add("chest-input-menu-btn-name")
            const span = document.createElement("div")
            nameBox.appendChild(span)
            if (name) {
                span.innerHTML = name
                btn.appendChild(nameBox)
            }
            
            if (type === "ctrl") {
                ctrl.push(btn)
            } else {
                btns.push(btn)
            }

            if (typeof tool.attachBtn === "function") {
                tool.attachBtn(btn)
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
            const toolData = data.input.message
            const inpContent = this.input.querySelector(".chest-input-message")
            for (const toolName in toolData) {
                const tool = this.tools[toolName]
                if (!tool) return
                
                if (typeof tool.write !== "function") return
                const rend = tool.write(toolData[toolName])
                if (!(rend instanceof HTMLElement)) return
                
                inpContent?.appendChild(rend)
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
            let lastMs = this.content.lastElementChild
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
    
    inputData(): Record<string, any> {
        const data = {
            data: {},
            side: "right"
        }
        
        const content = this.input.querySelector(".chest-message-content") as HTMLElement
        Array.from(content.children).forEach((box) => {
            const toolName = box.getAttribute("data-chest-tool")
            if (!toolName) return 
            const tool = this.tools[toolName]
            if (!tool) return
            if (typeof tool.send !== "function") return
            let data = tool.send(box)
            if (!data) return
            
            data.data[toolName] = data
        })
        
        return data
    }
    
    clearInput() {
        this.emit("clearInput")
        
        let content = this.input.querySelector(".chest-message-content")
        if (content) content.innerHTML = ""
    }
    
    send(data = this.inputData()) {
        const e = this.emit("send", { data: data })
        if (e.prevented) return
        this.clearInput()
        this.message(data)
    }
    
    save() {
        let data: Record<string, any> = {
            input: this.inputData(),
            messages: [],
        }
        
        Array.from(this.content.children).forEach((box) => {
            let msData: Record<string, any> = {
                id: Number(box.getAttribute("data-chest-id") as string),
                side: box.getAttribute("data-chest-direction") || "right",
                data: {},
            }
            
            const content = box.querySelector(".chest-message-content") as HTMLElement
            Array.from(content.children).forEach((toolBox) => {
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

