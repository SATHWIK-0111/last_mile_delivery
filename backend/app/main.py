from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import Base, engine
from app.models import User
from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router
from app.routes.agent import router as agent_router
from app.routes.orders import router as orders_router
from app.routes.agent import router as agent_router
Base.metadata.create_all(bind=engine)


app = FastAPI(
    title="Last-Mile Delivery Tracker",
    description="Delivery management platform API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "https://last-mile-delivery-frontend-xy8l.onrender.com",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(agent_router)
app.include_router(orders_router)

@app.get("/")
def root():
    return {
        "message": "Last-Mile Delivery Tracker API",
        "status": "running"
    }


@app.get("/health")
def health_check():
    return {
        "status": "healthy"
    }