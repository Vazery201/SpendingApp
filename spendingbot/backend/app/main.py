from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .routers import plaid

app = FastAPI(title="SpendingBot API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

app.include_router(plaid.router)
