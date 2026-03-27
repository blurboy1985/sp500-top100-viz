#!/usr/bin/env python3
"""
Phase 1: Data Acquisition for S&P 500 Top 20 Companies
Fetches TTM Revenue, TTM Net Profit, Market Cap, and 12-month price change
With improved rate limiting and bulk download
"""

import yfinance as yf
import json
import time
from datetime import datetime

# Top 20 S&P 500 companies by market cap
TICKERS = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "BRK-B", "TSLA",
    "UNH", "JNJ", "XOM", "JPM", "V", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "KO"
]

def fetch_bulk_data():
    """Fetch price history for all tickers at once."""
    print("Fetching bulk price history...")
    tickers_str = " ".join(TICKERS)
    try:
        # Download 1 year of data for all tickers at once
        hist = yf.download(tickers_str, period="1y", progress=False, group_by='ticker')
        return hist
    except Exception as e:
        print(f"Error in bulk download: {e}")
        return None

def fetch_ticker_info_sequential(tickers, delay=3):
    """Fetch ticker info one by one with delay."""
    results = []
    for ticker in tickers:
        try:
            print(f"Fetching {ticker}...", end=" ", flush=True)
            stock = yf.Ticker(ticker)
            info = stock.info
            
            # Extract needed fields
            data = {
                "ticker": ticker,
                "name": info.get("longName", info.get("shortName", ticker)),
                "market_cap": info.get("marketCap"),
                "ttm_revenue": info.get("totalRevenue"),
                "ttm_net_profit": info.get("netIncomeToCommon"),
            }
            
            # Check for missing critical data
            if all(v is not None for v in [data["market_cap"], data["ttm_revenue"], data["ttm_net_profit"]]):
                results.append(data)
                print(f"✓ Revenue: ${data['ttm_revenue']/1e9:.1f}B, Profit: ${data['ttm_net_profit']/1e9:.1f}B")
            else:
                print(f"⚠ Missing data")
                
        except Exception as e:
            print(f"✗ Error: {str(e)[:50]}")
        
        time.sleep(delay)
    
    return results

def calculate_price_changes(hist_data, tickers):
    """Calculate 12-month price changes from historical data."""
    changes = {}
    for ticker in tickers:
        try:
            if len(tickers) == 1:
                prices = hist_data['Close']
            else:
                prices = hist_data[ticker]['Close']
            
            if len(prices) >= 2:
                start_price = prices.iloc[0]
                end_price = prices.iloc[-1]
                change = ((end_price - start_price) / start_price) * 100
                changes[ticker] = round(change, 2)
        except Exception as e:
            print(f"Warning: Could not calculate price change for {ticker}: {e}")
            changes[ticker] = 0.0
    return changes

def main():
    print("=" * 60)
    print("S&P 500 Top 20 Data Acquisition")
    print("=" * 60)
    
    # Step 1: Bulk fetch price history (faster, less rate limit issues)
    print("\n[Step 1/2] Fetching price history in bulk...")
    price_changes = {}
    
    try:
        bulk_hist = yf.download(" ".join(TICKERS), period="1y", progress=False)
        print("✓ Price history downloaded")
        
        # Calculate price changes for each ticker
        for ticker in TICKERS:
            try:
                if len(TICKERS) == 1:
                    closes = bulk_hist['Close']
                else:
                    closes = bulk_hist[('Close', ticker)] if ('Close', ticker) in bulk_hist.columns else bulk_hist['Close']
                
                if len(closes) >= 2:
                    start = closes.iloc[0]
                    end = closes.iloc[-1]
                    price_changes[ticker] = round(((end - start) / start) * 100, 2)
                    print(f"  {ticker}: {price_changes[ticker]:+.1f}%")
            except Exception as e:
                print(f"  {ticker}: Error calculating price change")
                price_changes[ticker] = 0.0
    except Exception as e:
        print(f"Bulk download failed: {e}")
        print("Will fetch price changes individually...")
    
    # Step 2: Fetch fundamental data (with rate limiting)
    print("\n[Step 2/2] Fetching fundamental data (with rate limiting)...")
    results = []
    
    for i, ticker in enumerate(TICKERS):
        try:
            print(f"[{i+1}/20] Fetching {ticker}...", end=" ", flush=True)
            stock = yf.Ticker(ticker)
            info = stock.info
            
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
        except Exception as e:
            print(f"✗ {str(e)[:40]}")
        
        # Rate limiting - wait between requests
        if i < len(TICKERS) - 1:
            time.sleep(4)  # 4 seconds between requests
    
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
    
    output_path = "/root/.openclaw/workspace/sp500-top20/data.json"
    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)
    
    print(f"\nData saved to: {output_path}")
    return results

if __name__ == "__main__":
    main()