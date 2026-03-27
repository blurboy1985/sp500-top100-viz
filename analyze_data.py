#!/usr/bin/env python3
"""
Phase 2: Analysis of S&P 500 Top 100 Data
Extracts 10 key data-driven insights
"""

import json
from collections import defaultdict

def load_data():
    """Load the fetched data from JSON."""
    with open("/root/.openclaw/workspace/sp500-top100/data.json", "r") as f:
        return json.load(f)

def calculate_profit_margin(revenue, profit):
    """Calculate profit margin percentage."""
    if revenue and profit and revenue != 0:
        return round((profit / revenue) * 100, 2)
    return None

def analyze_data(data):
    """Extract 10 key insights from the data."""
    companies = data["companies"]
    insights = []
    
    # Calculate profit margins
    for c in companies:
        c["profit_margin"] = calculate_profit_margin(c["ttm_revenue"], c["ttm_net_profit"])
    
    # Sort by market cap for reference
    by_market_cap = sorted(companies, key=lambda x: x["market_cap"], reverse=True)
    by_revenue = sorted(companies, key=lambda x: x["ttm_revenue"], reverse=True)
    by_profit = sorted(companies, key=lambda x: x["ttm_net_profit"], reverse=True)
    by_margin = sorted(companies, key=lambda x: x["profit_margin"], reverse=True)
    by_price_change = sorted(companies, key=lambda x: x["price_change_12m"], reverse=True)
    
    # Insight 1: Highest profit margin
    highest_margin = by_margin[0]
    insights.append({
        "id": 1,
        "title": "Highest Profit Margin",
        "company": highest_margin["name"],
        "ticker": highest_margin["ticker"],
        "value": f"{highest_margin['profit_margin']:.1f}%",
        "detail": f"{highest_margin['name']} leads with a {highest_margin['profit_margin']:.1f}% profit margin, converting ${highest_margin['ttm_revenue']/1e9:.1f}B revenue into ${highest_margin['ttm_net_profit']/1e9:.1f}B profit."
    })
    
    # Insight 2: Lowest profit margin
    lowest_margin = by_margin[-1]
    insights.append({
        "id": 2,
        "title": "Lowest Profit Margin",
        "company": lowest_margin["name"],
        "ticker": lowest_margin["ticker"],
        "value": f"{lowest_margin['profit_margin']:.1f}%",
        "detail": f"{lowest_margin['name']} has the lowest margin at {lowest_margin['profit_margin']:.1f}%, with ${lowest_margin['ttm_revenue']/1e9:.1f}B revenue and ${lowest_margin['ttm_net_profit']/1e9:.1f}B profit."
    })
    
    # Insight 3: Top 5 by Market Cap
    top5_mcap = by_market_cap[:5]
    insights.append({
        "id": 3,
        "title": "Top 5 by Market Cap",
        "companies": [{"name": c["name"], "ticker": c["ticker"], "value": f"${c['market_cap']/1e12:.2f}T"} for c in top5_mcap],
        "detail": "These five companies represent the largest valuations in the S&P 500, dominating the tech and finance sectors."
    })
    
    # Insight 4: Top 5 by Revenue
    top5_rev = by_revenue[:5]
    insights.append({
        "id": 4,
        "title": "Top 5 by TTM Revenue",
        "companies": [{"name": c["name"], "ticker": c["ticker"], "value": f"${c['ttm_revenue']/1e9:.0f}B"} for c in top5_rev],
        "detail": "Revenue leaders show the scale of operations across retail, tech, and energy sectors."
    })
    
    # Insight 5: Top 5 by Net Profit
    top5_profit = by_profit[:5]
    insights.append({
        "id": 5,
        "title": "Top 5 by Net Profit",
        "companies": [{"name": c["name"], "ticker": c["ticker"], "value": f"${c['ttm_net_profit']/1e9:.0f}B"} for c in top5_profit],
        "detail": "These companies are the most profitable, generating the highest net income over the trailing twelve months."
    })
    
    # Insight 6: Best 12-month performer
    best_performer = by_price_change[0]
    insights.append({
        "id": 6,
        "title": "Best 12-Month Performer",
        "company": best_performer["name"],
        "ticker": best_performer["ticker"],
        "value": f"+{best_performer['price_change_12m']:.1f}%",
        "detail": f"{best_performer['name']} stock gained {best_performer['price_change_12m']:.1f}% over the past 12 months, the best performance among the top 20."
    })
    
    # Insight 7: Worst 12-month performer
    worst_performer = by_price_change[-1]
    insights.append({
        "id": 7,
        "title": "Worst 12-Month Performer",
        "company": worst_performer["name"],
        "ticker": worst_performer["ticker"],
        "value": f"{worst_performer['price_change_12m']:.1f}%",
        "detail": f"{worst_performer['name']} stock declined {abs(worst_performer['price_change_12m']):.1f}% over the past 12 months, reflecting sector or company-specific challenges."
    })
    
    # Insight 8: Average metrics
    avg_mcap = sum(c["market_cap"] for c in companies) / len(companies)
    avg_rev = sum(c["ttm_revenue"] for c in companies) / len(companies)
    avg_profit = sum(c["ttm_net_profit"] for c in companies) / len(companies)
    avg_margin = sum(c["profit_margin"] for c in companies) / len(companies)
    
    insights.append({
        "id": 8,
        "title": "Average Metrics (Top 100)",
        "metrics": {
            "avg_market_cap": f"${avg_mcap/1e12:.2f}T",
            "avg_revenue": f"${avg_rev/1e9:.0f}B",
            "avg_net_profit": f"${avg_profit/1e9:.0f}B",
            "avg_profit_margin": f"{avg_margin:.1f}%"
        },
        "detail": "The average top-100 S&P 500 company has significant market cap and generates substantial annual revenue."
    })
    
    # Insight 9: Revenue vs Market Cap outliers (using revenue-to-market-cap ratio)
    for c in companies:
        c["rev_to_mcap_ratio"] = c["ttm_revenue"] / c["market_cap"] if c["market_cap"] else 0
    
    by_ratio = sorted(companies, key=lambda x: x["rev_to_mcap_ratio"], reverse=True)
    high_ratio = by_ratio[0]
    low_ratio = by_ratio[-1]
    
    insights.append({
        "id": 9,
        "title": "Revenue vs Market Cap Outliers",
        "high": {
            "company": high_ratio["name"],
            "ticker": high_ratio["ticker"],
            "ratio": f"{high_ratio['rev_to_mcap_ratio']:.3f}",
            "detail": "Higher ratio suggests undervaluation relative to revenue"
        },
        "low": {
            "company": low_ratio["name"],
            "ticker": low_ratio["ticker"],
            "ratio": f"{low_ratio['rev_to_mcap_ratio']:.3f}",
            "detail": "Lower ratio suggests premium valuation or lower revenue efficiency"
        },
        "detail": "Revenue-to-market-cap ratio highlights potential valuation anomalies. A higher ratio may indicate undervaluation."
    })
    
    # Insight 10: Sector distribution (simplified based on company type)
    insights.append({
        "id": 10,
        "title": "Total Market Value of Top 100",
        "value": f"${sum(c['market_cap'] for c in companies)/1e12:.2f}T",
        "detail": f"The combined market capitalization of the top 100 S&P 500 companies is ${sum(c['market_cap'] for c in companies)/1e12:.2f} trillion, representing a significant portion of the entire index's value."
    })
    
    return insights

def generate_insights_json(insights):
    """Generate insights JSON for web display."""
    output = {
        "generated_at": data["fetch_date"],
        "insights": insights
    }
    return output

def main():
    global data
    print("=" * 60)
    print("S&P 500 Top 100 Analysis")
    print("=" * 60)
    
    data = load_data()
    print(f"Loaded {data['total_companies']} companies")
    
    insights = analyze_data(data)
    print(f"\nGenerated {len(insights)} insights:")
    
    for i in insights:
        print(f"\n{i['id']}. {i['title']}")
        if "value" in i:
            print(f"   → {i['value']}")
        elif "companies" in i:
            for c in i["companies"][:3]:
                print(f"   → {c['name']}: {c['value']}")
    
    # Save insights
    insights_data = generate_insights_json(insights)
    output_path = "/root/.openclaw/workspace/sp500-top100/insights.json"
    with open(output_path, "w") as f:
        json.dump(insights_data, f, indent=2)
    
    print(f"\n\nInsights saved to: {output_path}")
    return insights

if __name__ == "__main__":
    main()