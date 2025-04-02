import { Router, store } from "../libs/PageX"
import { shader, Theme, Pack } from "../libs/Shader"
import { req } from "../libs/Req"

export class App {
    main: HTMLElement = document.querySelector("main") as HTMLElement

    async init() {
        this.initApi()
        this.initToolbox()
        this.initRoutes()
        this.initDesign()
        const router = store.st.router
        router.navigate("/chat")
    }

    initApi() {
        req.config.options = {
            headers: {
                'Content-Type': 'application/json',
            }
        }
        
        // ЗАМЕНИ ЭТО НА ПРОДАКШЕНЕ
        req.config.conf.origin = 'http://127.0.0.1:8000'

        store.setState({
            req: req
        })
    }

    initToolbox() {
        store.setState({
            app: this,
            shader: shader,
            theme: Theme,
            pack: Pack,
        })
    }

    initRoutes() {
        const router = new Router()
        store.setState({
            router: router
        })

        router.add("/", () => import("../pages/RootPage"))
        
        router.add("/chat", () => import("../pages/ChatPage"))

        router.add("/*", () => import("../pages/NotFoundPage"))
    }

    initDesign() {
        this.loadSprite('/html/sprite.html')

        if (!shader.packs.rootPack) this.initColors()
        const packs = shader.packs
        
        let pack!: Record<string, any>
        for (let name in packs) {
            if (!pack) {
                pack = packs[name]
                continue
            }

            if (packs[name].config.priority > pack.config.priority) {
                pack = packs[name]
            }
        }

        pack = new Pack({ pack: pack })
        pack.init()

        if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) {
            document.documentElement.classList.add('dark-mode')
        } else {
            document.documentElement.classList.add('light-mode')
        }
    }

    initColors() {
        const root = new Theme("root")

        root.add(":root", {
            accent: "0, 122, 255",
            accentHover: "0, 95, 204",

            error: "255, 59, 48",
            success: "52, 199, 89",
            warning: "255, 149, 0",
            info: "0, 122, 255",

            white: "255, 255, 255",
            black: "0, 0, 0",

            transition: "cubic-bezier(0.25, 1, 0.5, 1)",
            transitionRe: "cubic-bezier(0.4, 0, 1, 1)",
        }, { toVar: true })
        
        root.add(".light-mode", {
            color: '0, 0, 0',  
            colorNd: '141, 141, 147',
            colorRd: '141, 141, 147',
            placeholder: '174, 174, 178', 

            bgSite: "242, 242, 247",
            bgSt: '229, 229, 234',
            bgNd: '209, 209, 214',
            bgRd: '199, 199, 204',

            component: '174, 174, 178',  
            componentd: '199, 199, 204',

            border: '216, 216, 220',
            borderNd: "199, 199, 204",
            borderRd: "174, 174, 178",

            opacity: "0.8",
        }, { toVar: true })

        root.add(".dark-mode", {
            color: '255, 255, 255',
            colorNd: '138, 138, 142',
            colorRd: '109, 109, 114',
            placeholder: '142, 142, 147',

            bgSite: '10, 10, 11',
            bgSt: '22, 22, 23',
            bgNd: '44, 44, 46',
            bgRd: '58, 58, 60',  

            component: '72, 72, 74',   
            componentNd: '99, 99, 102',

            border: '58, 58, 60',
            borderNd: '72, 72, 74',
            borderRd: '99, 99, 102',

            opacity: "0.5",
        }, { toVar: true })

        const rootPack = new Pack({
            name: "rootPack",
            themes: [root]
        })

        rootPack.config.priority = 0
        
        shader.savePack(rootPack)
    }
    
    createIcon(id: string):SVGSVGElement {
        if (id.slice(0, 1) !== "#") id = "#" + id
        const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg")
        const use = document.createElementNS("http://www.w3.org/2000/svg", "use")

        use.setAttributeNS("http://www.w3.org/1999/xlink", "xlink:href", `${id}`)
        svg.classList.add("icon")

        svg.appendChild(use)
        return svg
    }

    loadSprite(path: string) {
        fetch(path)
        .then((response) => response.text())
        .then((data) => {
            const sprite = document.createElement('div')
            sprite.innerHTML = data
            document.body.insertBefore(sprite, document.body.firstChild)
        })
    }

    async getHtml(url: string) {
        try {
            let res = await fetch(url)
            if (!res.ok) {
                return null
            }
            const html = res.text()
            return html
        } catch(e) {
            console.log("Ошибка при получении html: " + e)
            return null
        }
    }
}