import httpx
res = httpx.get('http://127.0.0.1:8000/get-housing', params={"data": "message"})
data = res.json()
print(data)