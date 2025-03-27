from fastapi import FastAPI
import uvicorn
from fastapi.middleware.cors import CORSMiddleware
from .routes import twilio_route, auth_route, subscription_route
from .models.base import Base
from .db.session import engine
from sqlalchemy import inspect

app = FastAPI(
    title="TimeGlobe WhatsApp Assistant",
    description="This Project aims to automate appointment booking through whatsapp",
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
Base.metadata.create_all(bind=engine)


# create customer table if not exists   
def create_customer_table():
    inspector = inspect(engine)
    if 'customers' not in inspector.get_table_names():
        Base.metadata.tables['customers'].create(bind=engine)


app.include_router(router=twilio_route.router, prefix="/api/twilio", tags=["Twilio"])
app.include_router(
    router=auth_route.router, prefix="/api/auth", tags=["authentication"]
)
app.include_router(
    router=subscription_route.router,
    prefix="/api/subscriptions",
    tags=["Subscriptions"],
)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0")
