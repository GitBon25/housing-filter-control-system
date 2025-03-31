export async function req(url: string | URL, options: RequestInit | Record<string, any> = {}) {
    const op = { ...req.config.options, ...options }

    if (!(url instanceof URL) && !url.startsWith("http")) {
        try {
            console.log(req.config.conf.origin + url)
            url = new URL(url, req.config.conf.origin)
        } catch(e) {
            console.error("[req] Error:", e)
            return
        }
    }

    try {
        const res = await fetch(url, op)
        
        if (!res.ok) throw new Error(`${res.status}: ${res.statusText}`)

        return res.json()
    } catch(e) {
        console.error("[req] Error:", e)
    }
}

req.config = {
    options: {},
    conf: {
        origin: location.origin
    }
}
