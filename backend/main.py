from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from db.database import create_tables
from routers.extraction import router

app = FastAPI(
    title="Logistics Document Extractor",
    description="LangGraph-powered AI agent for extracting and validating logistics documents",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    create_tables()

app.include_router(router)

@app.get("/health")
def health():
    return {"status": "ok", "service": "logistics-extractor"}
