#!/usr/bin/env python3
"""Build index.html with embedded data for Top 100."""
import json

with open('data.json') as f:
    data = json.load(f)
companies = data['companies']

with open('insights.json') as f:
    insights_data = json.load(f)
insights = insights_data.get('insights', insights_data)

html_template = '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>S&P 500 Top 100 - Interactive Visualization</title>
    <script src="https://cdn.plot.ly/plotly-2.27.0.min.js"></script>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
            color: #e8e8e8; min-height: 100vh; padding: 20px;
        }
        .container { max-width: 1400px; margin: 0 auto; }
        header { text-align: center; padding: 30px 20px; margin-bottom: 20px; }
        h1 { font-size: 2.5rem; font-weight: 700; color: #fff; margin-bottom: 10px; }
        .subtitle { font-size: 1rem; color: #a0a0a0; }
        .date-info { font-size: 0.85rem; color: #6a6a6a; margin-top: 5px; }
        .chart-container {
            background: rgba(255, 255, 255, 0.05); border-radius: 16px;
            padding: 20px; margin-bottom: 30px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        #bubble-chart { width: 100%; height: 700px; }
        .legend-info {
            display: flex; justify-content: center; gap: 30px;
            margin-top: 15px; font-size: 0.9rem; color: #a0a0a0;
        }
        .legend-item { display: flex; align-items: center; gap: 8px; }
        .insights-section {
            background: rgba(255, 255, 255, 0.05); border-radius: 16px;
            padding: 30px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        .insights-header { text-align: center; margin-bottom: 30px; }
        h2 { font-size: 1.8rem; color: #fff; }
        .insights-grid {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 20px;
        }
        .insight-card {
            background: rgba(255, 255, 255, 0.08); border-radius: 12px; padding: 20px;
            border-left: 4px solid; transition: transform 0.2s, box-shadow 0.2s;
        }
        .insight-card:hover { transform: translateY(-3px); box-shadow: 0 6px 15px rgba(0, 0, 0, 0.4); }
        .insight-card.positive { border-left-color: #00c853; }
        .insight-card.negative { border-left-color: #ff5252; }
        .insight-card.neutral { border-left-color: #448aff; }
        .insight-card.highlight { border-left-color: #ffd700; }
        .insight-number { font-size: 0.75rem; color: #6a6a6a; margin-bottom: 5px; }
        .insight-title { font-size: 1.1rem; font-weight: 600; color: #fff; margin-bottom: 10px; }
        .insight-value { font-size: 1.5rem; font-weight: 700; color: #00c853; margin-bottom: 10px; }
        .insight-value.negative { color: #ff5252; }
        .insight-company { font-size: 0.9rem; color: #a0a0a0; margin-bottom: 8px; }
        .insight-detail { font-size: 0.85rem; color: #888; line-height: 1.4; }
        .insight-list { list-style: none; margin-top: 10px; }
        .insight-list li {
            padding: 5px 0; font-size: 0.85rem; display: flex; justify-content: space-between;
        }
        .insight-list .company-name { color: #a0a0a0; }
        .insight-list .company-value { color: #fff; font-weight: 500; }
        .metrics-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 10px; margin-top: 10px; }
        .metric-item { text-align: center; padding: 10px; background: rgba(0, 0, 0, 0.2); border-radius: 8px; }
        .metric-label { font-size: 0.75rem; color: #6a6a6a; }
        .metric-value { font-size: 1rem; color: #fff; font-weight: 600; }
        .outlier-container { display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin-top: 10px; }
        .outlier-box { padding: 10px; background: rgba(0, 0, 0, 0.2); border-radius: 8px; }
        .outlier-label { font-size: 0.75rem; color: #6a6a6a; }
        .outlier-company { font-size: 0.9rem; color: #fff; }
        .outlier-ratio { font-size: 1rem; font-weight: 600; color: #448aff; }
        footer { text-align: center; padding: 30px 20px; margin-top: 20px; color: #6a6a6a; font-size: 0.85rem; }
        @media (max-width: 768px) {
            h1 { font-size: 1.8rem; } #bubble-chart { height: 400px; }
            .insights-grid { grid-template-columns: 1fr; } .legend-info { flex-direction: column; gap: 10px; }
            .outlier-container { grid-template-columns: 1fr; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>S&P 500 Top 100 Companies</h1>
            <p class="subtitle">Interactive Bubble Chart Visualization</p>
            <p class="date-info">Data as of March 2026 | Market Cap, Revenue, Profit & 12-Month Performance</p>
        </header>
        <div class="chart-container">
            <div id="bubble-chart"></div>
            <div class="legend-info">
                <div class="legend-item">
                    <span style="font-size: 0.85em;">💡 Bubble Size = Market Cap | Color = 12M Price Change (see colorbar)</span>
                </div>
            </div>
        </div>
        <div class="insights-section">
            <div class="insights-header"><h2>10 Key Findings</h2></div>
            <div class="insights-grid" id="insights-grid"></div>
        </div>
        <footer>
            <p>Data sourced from public financial reports | Visualization generated March 2026</p>
        </footer>
    </div>
    <script>
        const companies = COMPANIES_DATA;
        const insights = INSIGHTS_DATA;
        
        function formatBillions(v) { return (v / 1e9).toFixed(1) + 'B'; }
        function formatTrillions(v) { return (v / 1e12).toFixed(2) + 'T'; }
        
        function createBubbleChart() {
            const xValues = companies.map(c => c.ttm_revenue / 1e9);
            const yValues = companies.map(c => c.ttm_net_profit / 1e9);
            const sizes = companies.map(c => Math.log10(c.market_cap / 1e9) * 8);
            const priceChanges = companies.map(c => c.price_change_12m);
            
            const trace = {
                x: xValues, y: yValues, mode: 'markers+text', type: 'scatter',
                text: companies.map(c => c.ticker), textposition: 'top center',
                textfont: {color: '#fff', size: 10, family: 'monospace'},
                hovertemplate: '<b>%{text}</b><br>%{customdata.name}<br><br>Revenue: $%{customdata.revenue}B<br>Net Profit: $%{customdata.profit}B<br>Market Cap: $%{customdata.mcap}T<br>12M Change: %{customdata.change}%<extra></extra>',
                customdata: companies.map(c => ({
                    name: c.name, revenue: (c.ttm_revenue / 1e9).toFixed(1),
                    profit: (c.ttm_net_profit / 1e9).toFixed(1),
                    mcap: (c.market_cap / 1e12).toFixed(2),
                    change: c.price_change_12m > 0 ? '+' + c.price_change_12m.toFixed(1) : c.price_change_12m.toFixed(1)
                })),
                marker: {
                    size: sizes, color: priceChanges,
                    colorscale: [[-1, '#ff1744'], [-0.5, '#ff5252'], [-0.25, '#ff8a80'], [0, '#ffffff'], [0.25, '#a5d6a7'], [0.5, '#66bb6a'], [1, '#00c853']],
                    colorbar: { title: '12M Change %', titleside: 'right', titlefont: {color: '#a0a0a0', size: 12}, tickfont: {color: '#a0a0a0'}, len: 0.6, thickness: 20 },
                    line: { color: 'rgba(255, 255, 255, 0.5)', width: 1.5 }, sizemode: 'diameter', sizemin: 8, sizeref: 0.5
                }
            };
            
            const layout = {
                title: { text: 'TTM Revenue vs Net Profit (Bubble Size = Market Cap)', font: {color: '#fff', size: 18} },
                xaxis: { title: {text: 'TTM Revenue ($ Billions)', font: {color: '#a0a0a0'}}, type: 'log', gridcolor: 'rgba(255, 255, 255, 0.1)', tickfont: {color: '#a0a0a0'} },
                yaxis: { title: {text: 'TTM Net Profit ($ Billions)', font: {color: '#a0a0a0'}}, gridcolor: 'rgba(255, 255, 255, 0.1)', tickfont: {color: '#a0a0a0'} },
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', hovermode: 'closest', margin: {l: 80, r: 100, t: 60, b: 60}
            };
            Plotly.newPlot('bubble-chart', [trace], layout, {responsive: true});
        }
        
        function renderInsights() {
            const grid = document.getElementById('insights-grid');
            insights.forEach(insight => {
                const card = document.createElement('div');
                card.className = `insight-card ${insight.type || 'neutral'}`;
                let content = `<div class="insight-number">Insight #${insight.id}</div>`;
                content += `<div class="insight-title">${insight.title}</div>`;
                if (insight.value) {
                    const valueClass = insight.type === 'negative' ? 'negative' : '';
                    content += `<div class="insight-value ${valueClass}">${insight.value}</div>`;
                }
                if (insight.company) {
                    content += `<div class="insight-company">${insight.company} (${insight.ticker})</div>`;
                }
                if (insight.companies) {
                    content += '<ul class="insight-list">';
                    insight.companies.forEach(c => {
                        content += `<li><span class="company-name">${c.name} (${c.ticker})</span><span class="company-value">${c.value}</span></li>`;
                    });
                    content += '</ul>';
                }
                if (insight.metrics) {
                    content += '<div class="metrics-grid">';
                    Object.entries(insight.metrics).forEach(([label, value]) => {
                        content += `<div class="metric-item"><div class="metric-label">${label.replace('avg_', 'Avg ').replace('_', ' ')}</div><div class="metric-value">${value}</div></div>`;
                    });
                    content += '</div>';
                }
                if (insight.high && insight.low) {
                    content += `<div class="outlier-container">
                        <div class="outlier-box"><div class="outlier-label">High Ratio</div><div class="outlier-company">${insight.high.company} (${insight.high.ticker})</div><div class="outlier-ratio">${insight.high.ratio}</div></div>
                        <div class="outlier-box"><div class="outlier-label">Low Ratio</div><div class="outlier-company">${insight.low.company} (${insight.low.ticker})</div><div class="outlier-ratio">${insight.low.ratio}</div></div>
                    </div>`;
                }
                content += `<div class="insight-detail">${insight.detail}</div>`;
                card.innerHTML = content;
                grid.appendChild(card);
            });
        }
        document.addEventListener('DOMContentLoaded', () => { createBubbleChart(); renderInsights(); });
    </script>
</body>
</html>
'''

# Replace placeholders
html = html_template.replace('COMPANIES_DATA', json.dumps(companies, indent=8))
html = html.replace('INSIGHTS_DATA', json.dumps(insights, indent=8))

with open('index.html', 'w') as f:
    f.write(html)

print(f"✅ Built index.html with {len(companies)} companies and {len(insights)} insights")
