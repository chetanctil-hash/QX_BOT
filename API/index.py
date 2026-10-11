from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import yfinance as yf
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime, timedelta

from providers import YFinanceProvider
from engines.scoring_engine import ScoringEngine
from engines.allocation_engine import AllocationEngine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- QUANT CONFIGURATION ---
BENCHMARK = "^NSEI"  # Nifty 50
Sectors = {
    'Specialty Chem': 'Chem',
    'Housing Finance': 'Financials',
    'Pharma/CDMO': 'Pharma',
    'Defence': 'Defence',
    'BFSI': 'Financials',
    'Auto Ancillary': 'Auto',
    'Electronics Mfg': 'Electronics',
    'Infra/Pipes': 'Infra',
    'Energy Logistics': 'Energy',
    'IT Services': 'IT',
    'Real Estate': 'Real Estate',
    'Engineering & Capital Goods': 'Engineering',
    'Abrasives': 'Abrasives'
}

# DB Path
DB_PATH = "qx_terminal.db"

def get_market_regime():
    """Quant Regime Detection: Bullish if Nifty 50 > 200DMA"""
    try:
        bench = yf.Ticker(BENCHMARK)
        hist = bench.history(period='1y')
        sma200 = hist['Close'].rolling(window=200).mean().iloc[-1]
        current = hist['Close'].iloc[-1]
        return {
            'regime': 'BULLISH' if current > sma200 else 'BEARISH',
            'benchmark_price': float(current),
            'sma200': float(sma200)
        }
    except:
        return {'regime': 'NEUTRAL', 'benchmark_price': 0, 'sma200': 0}

@app.get("/api/market")
async def get_market_status():
    return get_market_regime()

@app.get("/api/portfolio")
async def get_portfolio():
    """
    Refactored Portfolio Endpoint:
    Fetches holdings from DB, calculates live metrics, and uses AllocationEngine for target weights.
    """
    provider = YFinanceProvider()
    alloc_eng = AllocationEngine(provider=provider, db_path=DB_PATH)
    scoring_eng = ScoringEngine(db_path=DB_PATH)

    try:
        # 1. Fetch Holdings from DB
        conn = sqlite3.connect(DB_PATH)
        # Join with instruments to get metadata (name, cluster)
        query = '''
            SELECT p.symbol, p.quantity, p.avg_cost, i.name, i.cluster
            FROM portfolio p
            JOIN instruments i ON p.symbol = i.symbol
        '''
        df_pf = pd.read_sql_query(query, conn)
        conn.close()

        if df_pf.empty:
            return []

        symbols = df_pf['symbol'].tolist()

        # 2. Calculate Target Weights via AllocationEngine
        target_weights = alloc_eng.calculate_target_weights(symbols)

        # 3. Process each holding
        updated_pf = []
        for _, row in df_pf.iterrows():
            sym = row['symbol']
            qty = row['quantity']
            avg = row['avg_cost']

            # Get live price
            ticker = yf.Ticker(sym)
            ltp = ticker.fast_info['last_price']

            inv = qty * ltp
            pl = inv - (qty * avg)
            ret = (pl / (qty * avg)) * 100 if avg > 0 else 0

            # Get Quant Metrics for the row (matching frontend expected structure)
            score_data = scoring_eng.calculate_composite_score(sym)

            # Map to frontend: 'mom' and 'qs'
            mom_data = {'score': score_data['mom_score'] if score_data else 50,
                        'rs': 0, # simplified for endpoint
                        'vol': 0}

            qs_data = {
                'mom': (score_data['mom_score'] if score_data else 50) // 5,
                'vola': 0,
                'rstr': (score_data['composite_score'] if score_data else 50) // 10
            }

            updated_pf.append({
                'sym': sym,
                'name': row['name'],
                'cluster': row['cluster'],
                'qty': qty,
                'avg': avg,
                'ltp': ltp,
                'inv': inv,
                'pl': pl,
                'ret': ret,
                'mom': mom_data,
                'qs': qs_data,
                'target_weight': round(target_weights.get(sym, 0) * 100, 2),
                'volatility': alloc_eng._calculate_annualized_volatility(sym)
            })

        return updated_pf

    except Exception as e:
        print(f"Portfolio Error: {e}")
        return []

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
