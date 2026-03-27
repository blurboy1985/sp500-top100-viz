#!/usr/bin/env python3
"""
Phase 1: Data Acquisition for S&P 500 Top 100 Companies
Fetches TTM Revenue, TTM Net Profit, Market Cap, and 12-month price change
With improved rate limiting and batch processing
"""

import yfinance as yf
import json
import time
from datetime import datetime

# Top 100 S&P 500 companies by market cap
TICKERS = [
    "NVDA", "AAPL", "GOOGL", "MSFT", "AMZN", "META", "BRK-B", "TSLA",
    "UNH", "JNJ", "XOM", "JPM", "V", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "KO",
    "PEP", "COST", "WMT", "MCD", "TMO", "ADBE", "CSCO", "ACN", "AVGO", "NKE",
    "DHR", "TXN", "LIN", "ORCL", "WFC", "BAC", "ABT", "CRM", "DIS",
    "VZ", "CMCSA", "AMD", "INTC", "QCOM", "T", "UBER", "NFLX", "HON", "UPS",
    "PM", "MS", "GS", "CAT", "BA", "GE", "DE", "SPGI", "BLK", "GILD",
    "AXON", "ISRG", "SYK", "BKNG", "ADP", "TJX", "LLY", "ZTS", "REGN", "VRTX",
    "PLD", "AMT", "CB", "SCHW", "MDLZ", "TMUS", "FI", "AON", "CL", "EQIX",
    "ITW", "APD", "CME", "HCA", "MU", "PGR", "CSX", "NSC", "WM", "FCX",
    "EMR", "SHW", "MCO", "ICE", "GD", "ATVI", "F", "GM", "TGT", "DUK",
    "SO", "BMY", "PNC", "USB", "TFC"
]

def fetch_bulk_price_history():
    """Fetch price history for all tickers at once."""
    print("Fetching bulk price history...")
    tickers_str = " ".join(TICKERS)
    try:
        # Download 1 year of data for all tickers at once
        hist = yf.download(tickers_str, period="1y", progress=False)
        print("✓ Price history downloaded")
        return hist
    except Exception as e:
        print(f"Error in bulk download: {e}")
        return None

def calculate_price_changes(hist_data):
    """Calculate 12-month price changes from historical data."""
    changes = {}
    
    # Handle different column structures
    if 'Close' in hist_data.columns:
        close_data = hist_data['Close']
        
        # Check if it's multi-index (multiple tickers)
        if isinstance(close_data.columns, pd.MultiIndex):
            for ticker in TICKERS:
                if ticker in close_data.columns:
                    prices = close_data[ticker]
                    if len(prices) >= 2 and prices.iloc[0] > 0:
                        start_price = prices.iloc[0]
                        end_price = prices.iloc[-1]
                        change = ((end_price - start_price) / start_price) * 100
                        changes[ticker] = round(change, 2)
        else:
            # Single ticker or flat structure
            prices = close_data
            if len(prices) >= 2 and prices.iloc[0] > 0:
                start_price = prices.iloc[0]
                end_price = prices.iloc[-1]
                change = ((end_price - start_price) / start_price) * 100
                # If it's a single ticker case, this won't work for 100
                # We need to handle multi-index properly
    
    return changes

def fetch_info_with_retry(ticker, max_retries=3, base_delay=5):
    """Fetch ticker info with retry logic."""
    for attempt in range(max_retries):
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Check for valid data
            if info and 'marketCap' in info:
                return info
            else:
                print(f"    Attempt {attempt+1}: No valid data for {ticker}")
        except Exception as e:
            print(f"    Attempt {attempt+1}: Error - {str(e)[:50]}")
        
        if attempt < max_retries - 1:
            time.sleep(base_delay * (attempt + 1))
    
    return None

def main():
    import pandas as pd
    
    print("=" * 60)
    print("S&P 500 Top 100 Data Acquisition")
    print("=" * 60)
    
    # Step 1: Bulk fetch price history
    print("\n[Step 1] Fetching price history in bulk...")
    price_changes = {}
    
    try:
        bulk_hist = yf.download(" ".join(TICKERS), period="1y", progress=False, group_by='ticker')
        print("✓ Price history downloaded")
        
        # Calculate price changes for each ticker
        for ticker in TICKERS:
            try:
                if len(TICKERS) == 1:
                    closes = bulk_hist['Close']
                else:
                    # Try different column access patterns
                    if ticker in bulk_hist.columns:
                        closes = bulk_hist[ticker]['Close']
                    elif ('Close', ticker) in bulk_hist.columns:
                        closes = bulk_hist['Close'][ticker]
                    elif hasattr(bulk_hist['Close'], 'columns') and ticker in bulk_hist['Close'].columns:
                        closes = bulk_hist['Close'][ticker]
                    else:
                        continue
                
                if len(closes) >= 2:
                    start = closes.iloc[0]
                    end = closes.iloc[-1]
                    if start > 0:
                        price_changes[ticker] = round(((end - start) / start) * 100, 2)
                        print(f"  {ticker}: {price_changes[ticker]:+.1f}%")
            except Exception as e:
                print(f"  {ticker}: Could not calculate price change")
    except Exception as e:
        print(f"Bulk download failed: {e}")
    
    # Step 2: Fetch fundamental data in batches with long delays
    print("\n[Step 2] Fetching fundamental data (batch mode with delays)...")
    results = []
    batch_size = 5
    batch_delay = 60  # Wait 60 seconds between batches
    
    for batch_start in range(0, len(TICKERS), batch_size):
        batch = TICKERS[batch_start:batch_start + batch_size]
        print(f"\nBatch {batch_start//batch_size + 1}/{len(TICKERS)//batch_size + 1}: {batch}")
        
        for ticker in batch:
            try:
                print(f"  Fetching {ticker}...", end=" ", flush=True)
                stock = yf.Ticker(ticker)
                info = stock.info
                
                if info:
                    data = {
                        "ticker": ticker,
                        "name": info.get("longName", info.get("shortName", ticker)),
                        "market_cap": info.get("marketCap"),
                        "ttm_revenue": info.get("totalRevenue"),
                        "ttm_net_profit": info.get("netIncomeToCommon"),
                        "price_change_12m": price_changes.get(ticker, 0.0)
                    }
                    
                    # Check for missing critical data
                    missing = [k for k, v in [("market_cap", data["market_cap"]), 
                                               ("ttm_revenue", data["ttm_revenue"]), 
                                               ("ttm_net_profit", data["ttm_net_profit"])] if v is None]
                    
                    if not missing:
                        results.append(data)
                        print(f"✓ MCAP: ${data['market_cap']/1e12:.2f}T, Rev: ${data['ttm_revenue']/1e9:.0f}B")
                    else:
                        print(f"⚠ Missing: {missing}")
                else:
                    print("✗ No info returned")
                    
            except Exception as e:
                print(f"✗ {str(e)[:40]}")
            
            # Delay between individual requests within batch
            time.sleep(3)
        
        # Wait longer between batches to avoid rate limits
        if batch_start + batch_size < len(TICKERS):
            print(f"  Waiting {batch_delay}s before next batch...")
            time.sleep(batch_delay)
    
    # Summary
    print("\n" + "=" * 60)
    print(f"Successfully fetched: {len(results)}/{len(TICKERS)} tickers")
    
    if len(results) < len(TICKERS):
        failed = [t for t in TICKERS if t not in [r["ticker"] for r in results]]
        print(f"Failed: {failed}")
    
    # Save to JSON
    output = {
        "fetch_date": datetime.now().isoformat(),
        "total_companies": len(results),
        "companies": results
    }
    
    output_path = "/root/.openclaw/workspace/sp500-top100/data.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nData saved to: {output_path}")
    return results

if __name__ == "__main__":
    main()