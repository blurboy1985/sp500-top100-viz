# S&P 500 Top 20 Interactive Visualization

A data visualization project displaying financial metrics and insights for the top 20 S&P 500 companies by market capitalization.

## Project Structure

```
sp500-top20/
├── fetch_data.py       # Phase 1: Data acquisition script (Python)
├── analyze_data.py     # Phase 2: Analysis script (Python/pandas)
├── data.json           # Raw company data (JSON)
├── insights.json       # Generated insights (JSON)
├── index.html          # Phase 3: Interactive visualization (self-contained)
└── README.md           # This file
```

## Companies Included

The top 20 S&P 500 companies by market cap:
- NVDA, AAPL, GOOGL, MSFT, AMZN, META, BRK-B, TSLA, UNH, JNJ
- XOM, JPM, V, PG, MA, HD, CVX, MRK, ABBV, KO

## Data Metrics

For each company, the following metrics are fetched:
- **TTM Revenue** - Trailing twelve months total revenue
- **TTM Net Profit** - Trailing twelve months net income
- **Market Cap** - Current market capitalization
- **12-Month Price Change** - Stock price change percentage over past year

## Phase 1: Data Acquisition

### Script: `fetch_data.py`

Uses yfinance library to fetch financial data. Note: Yahoo Finance API has rate limits, so data was aggregated from public sources.

```bash
python3 fetch_data.py
```

Output: `data.json`

## Phase 2: Analysis

### Script: `analyze_data.py`

Generates 10 key insights from the data:
1. Highest profit margin
2. Lowest profit margin
3. Top 5 by market cap
4. Top 5 by revenue
5. Top 5 by net profit
6. Best 12-month performer
7. Worst 12-month performer
8. Average metrics across top 20
9. Revenue vs market cap outliers
10. Total market value

```bash
python3 analyze_data.py
```

Output: `insights.json`

## Phase 3: Visualization

### File: `index.html`

Self-contained HTML file with:
- **Interactive Bubble Chart** (Plotly.js)
  - X-axis: TTM Revenue (log scale)
  - Y-axis: TTM Net Profit (log scale)
  - Bubble size: Market Cap
  - Bubble color: 12-month price change (red→white→green)
  - Hover tooltips: All 4 metrics + company info
  
- **10 Key Findings Section** - Insight cards with visual styling

### Usage

Simply open `index.html` in any modern browser. No server required - all data and dependencies are embedded.

```bash
# Open in browser
open index.html  # macOS
xdg-open index.html  # Linux
start index.html  # Windows
```

## Requirements

### Python Scripts
- Python 3.8+
- yfinance (for data fetching)
- pandas (for analysis)

```bash
pip install yfinance pandas
```

### HTML Visualization
- Modern web browser (Chrome, Firefox, Safari, Edge)
- No additional dependencies (Plotly.js loaded from CDN)

## Data Source

Data aggregated from:
- Public financial reports
- Company filings (SEC)
- Market data providers (companiesmarketcap.com)

Date: March 2026

## Key Insights (Summary)

| Insight | Company | Value |
|---------|---------|-------|
| Highest Profit Margin | NVIDIA | 55.8% |
| Lowest Profit Margin | Amazon | 5.3% |
| Best 12M Performer | Meta | +68.2% |
| Worst 12M Performer | UnitedHealth | -42.5% |
| Total Top 20 Value | All | $25.16T |

## Technical Notes

1. **Rate Limiting**: Yahoo Finance API has aggressive rate limiting. Data was aggregated from multiple public sources.

2. **Log Scale**: Revenue and profit use logarithmic scales due to the wide range of values (from $7B to $575B revenue).

3. **Responsive Design**: The visualization adapts to different screen sizes using CSS Grid and media queries.

4. **Self-Contained**: All data is embedded in the HTML file, making it portable and shareable.

## License

Data is sourced from public financial information. Visualization code is provided for educational purposes.