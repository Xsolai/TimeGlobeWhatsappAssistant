from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from .api.v1.endpoints import twilio_route, time_globe_routes
import logging

app = FastAPI(
    title="WhatsApp Automation", description="whatsapp automation with twilio"
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router=twilio_route.router, prefix="/api/v1/twilio", tags=["Twilio"])
app.include_router(
    router=time_globe_routes.router, prefix="/api/v1/time-globe", tags=["Time Globe"]
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
