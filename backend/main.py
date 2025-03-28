from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from auth.routes import auth_router
from admin.routes import admin_router
from chat.routes import chat_router
from docs_management.routes import docs_router
from user.routes import user_router
from db.main import init_db

@asynccontextmanager 
async def life_span(app:FastAPI):
    print(f"Server is starting...")
    await init_db()
    yield
    print(f"Server has been stopped")

app = FastAPI(
    title="Engineering Support AI Chatbot",
    version="1.0.0",
    lifespan=life_span,
    description=(
        "The Engineering Support AI Chatbot is a custom-built, self-hosted chatbot designed to assist field engineers with real-time technical support. "
        "It leverages AI-powered natural language processing (NLP) to provide accurate, context-aware answers based on an organization's internal documentation."
    )
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(auth_router, tags=['auth'])
app.include_router(admin_router, tags=['admin'])
app.include_router(chat_router, tags=['chat'])
app.include_router(docs_router, tags=['docs'])
app.include_router(user_router, tags=['user'])

@app.get("/")
async def root():
    return {
        "message": "Welcome to the Engineering Support AI Chatbot API!",
        "project": "Engineering Support AI Chatbot API",
        "version": app.version,
        "description": app.description,
        "documentation": {
            "swagger": "/docs",
            "redoc": "/redoc"
        }
    }

