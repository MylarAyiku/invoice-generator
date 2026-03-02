from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routes import invoices, pdf

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Invoice Generator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(invoices.router, prefix="/api/invoices", tags=["invoices"])
app.include_router(pdf.router, prefix="/api/pdf", tags=["pdf"])

@app.get("/api/health")
def health():
    return {"status": "ok"}