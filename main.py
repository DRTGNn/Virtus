
from fastapi import FastAPI, Request
from pydantic import BaseModel
from backend.schemas import RequestVirtus
from backend.routers import router_user, router_conversation, router_message, router_Virtus  
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from backend.routers import router_user, router_conversation, router_message

app = FastAPI(title="Grete, mio Virtus!")

app.include_router(router_Virtus)
app.include_router(router_user)
app.include_router(router_conversation)
app.include_router(router_message)








