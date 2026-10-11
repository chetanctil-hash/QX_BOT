import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
from providers import YFinanceProvider
from engines.breakout_engine import BreakoutEngine
from engines.scoring_engine import ScoringEngine

def log_rejection(symbol, reason, filter_type, price=None):
    """Persists rejected candidates to the audit trail."""
    try:
        conn = sqlite3.connect("qx_terminal.db")
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO rejected_candidates (symbol, timestamp, filter_failed, reason, price_at_rejection)
            VALUES (?, ?, ?, ?, ?)
        ''', (symbol, datetime.now().isoformat(), filter_type, reason, price))
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Rejection Logging Error: {e}")

def run_quant_screen():
    print("Initializing QX-8.0 Quantamental Screen...")

    provider = YFinanceProvider()
    breakout_eng = BreakoutEngine(provider=provider)
    scoring_eng = ScoringEngine(provider=provider)

    # Sample Universe of NSE stocks for testing
    universe = [
        'HAL.NS', 'DIXON.NS', 'BHEL.NS', 'TATAELXSI.NS',
        'BEL.NS', 'CDSL.NS', 'KEI.NS', 'MazagonDock.NS'
    ]

    breakouts = []
    print("\n--- Step 1: 52-Week Breakout Filter ---")
    for sym in universe:
        # Mock market cap for testing (in cr)
        mcap = 10000
        res = breakout_eng.evaluate_breakout(sym, mcap)
        if res['satisfied']:
            print(f"[MATCH] {sym} passed 52W Breakout")
            breakouts.append(sym)
        else:
            print(f"[SKIP] {sym}: {res['reason']}")
            log_rejection(sym, res['reason'], "BREAKOUT")

    if not breakouts:
        print("\nNo breakouts found in current universe.")
        return

    print("\n--- Step 2: QX-8.0 Quantamental Scoring ---")
    final_rankings = []
    for sym in breakouts:
        score_data = scoring_eng.calculate_composite_score(sym)
        if score_data:
            # Threshold check: only a high-quality breakout is an actionable signal
            if score_data['composite_score'] >= 60:
                print(f"[SCORE] {sym}: {score_data['composite_score']:.2f} -> ACTIONABLE")
                # Use the latest price for the signal price
                try:
                    import yfinance as yf
                    price = yf.Ticker(sym).fast_info['last_price']
                except: price = None

                scoring_eng.save_signal(score_data, action="BUY", signal_price=price)
                final_rankings.append(score_data)
            else:
                print(f"[SKIP] {sym}: {score_data['composite_score']:.2f} (Low Quality)")
                log_rejection(sym, f"Score {score_data['composite_score']:.2f} below 60", "SCORING")

    # Rank by composite score
    final_rankings.sort(key=lambda x: x['composite_score'], reverse=True)

    print("\n--- Final QX-8.0 Priority List ---")
    for i, stock in enumerate(final_rankings, 1):
        print(f"{i}. {stock['symbol']} - Score: {stock['composite_score']:.2f}")

if __name__ == "__main__":
    run_quant_screen()
