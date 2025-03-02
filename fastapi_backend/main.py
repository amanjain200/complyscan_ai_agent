from fastapi import FastAPI
from routers import items
from fastapi.middleware.cors import CORSMiddleware
from routers.chats import router as chats_router

app = FastAPI(title="My FastAPI Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins="*",  # Allow specified origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

# Include routers
app.include_router(chats_router, prefix="", tags=["Chats"])
app.include_router(items.router, prefix="/items", tags=["Items"])

@app.get("/")
def home():
    return {"message": "Welcome to FastAPI Backend!"}
