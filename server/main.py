from fastapi import FastAPI
from ai.api import getHouing


app = FastAPI()

@app.get("/get-housing")
async def housing(data: str):
    return {
        'link': "no-link",
        "header": "dom v moskve",
        "main": 'bolishoy dom',
        "fromReq": data
    }

