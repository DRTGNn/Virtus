
from fastapi import FastAPI
from backend.routers import router_user, router_conversation, router_message, router_Virtus
from Database.db import Base, engine 

app = FastAPI(title="Grete, mio Virtus!")

Base.metadata.create_all(bind=engine)

app.include_router(router_Virtus)
app.include_router(router_user)
app.include_router(router_conversation)
app.include_router(router_message)








