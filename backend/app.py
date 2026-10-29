from fastapi import FastAPI
from backend.api.routes import router

app = FastAPI(title="Modular AI Website Builder API", version="1.0.0")
app.include_router(router)
