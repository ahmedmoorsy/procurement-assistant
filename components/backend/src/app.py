from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.routes import router
from services.mognodb_service import MongoDBService
from config import Config


@asynccontextmanager
async def lifespan(app: FastAPI):
    config = Config()
    mongo_client = MongoDBService(
        host=config.mongodb.HOST,
        port=config.mongodb.PORT,
        username=config.mongodb.USERNAME,
        password=config.mongodb.PASSWORD,
        db_name=config.mongodb.DB_NAME,
        orders_collection="Orders",
    )
    app.state.mongo_client = mongo_client
    yield
    await mongo_client.close_connection()


app = FastAPI(
    title="Procurement Chatbot Assistant",
    description="This is the backend service for the Procurement Chatbot Assistant.",
    lifespan=lifespan,
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(router)


@app.get("/")
async def health_check():
    return "Welcome to the Procurement Chatbot Assistant!"
