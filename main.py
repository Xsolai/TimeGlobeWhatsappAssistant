from fastapi import FastAPI, Request

app = FastAPI()

@app.post("/incomingwhatsapp")
async def whatsapp_webhook(request: Request):
    payload = await request.json()
    # print("📦 Incoming webhook from 360dialog:", payload)
    return {"status": "ok"}  # Must return 200 OK
