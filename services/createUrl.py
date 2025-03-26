def createUrl(params, config = {}):
    conf = {
        "site": "https://domclick.ru/search"
    } | config

    query = "?"

    prms = []
    for key in params.keys():
        vl = params[key]
        prms.append(key + "=" + vl)
    
    query += "&".join(prms)

    if (query == "?"): return conf['site']

    res = conf['site'] + query
    return res

print(createUrl({ "town": "Moscow", "price": "300000009000000"}))