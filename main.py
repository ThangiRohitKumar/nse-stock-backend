from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nse_agent import NSEMarketAgent

app = FastAPI()
agent = NSEMarketAgent()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to Lovable domain
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "NSE AI Agent is Live!"}

@app.get("/analyze/{symbol}")
def analyze_stock(symbol: str):
    return agent.generate_stock_report(symbol)
