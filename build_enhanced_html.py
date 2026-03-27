#!/usr/bin/env python3
"""Build enhanced index.html with filters, ranking table, and dynamic insights."""
import json

with open('data.json') as f:
    data = json.load(f)
companies = data['companies']

with open('insights.json') as f:
    insights_data = json.load(f)
insights = insights_data.get('insights', insights_data)

html = '''<!DOCTYPE html>
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
        .container { max-width: 1600px; margin: 0 auto; }
        header { text-align: center; padding: 30px 20px; margin-bottom: 20px; }
        h1 { font-size: 2.5rem; font-weight: 700; color: #fff; margin-bottom: 10px; }
        .subtitle { font-size: 1rem; color: #a0a0a0; }
        .date-info { font-size: 0.85rem; color: #6a6a6a; margin-top: 5px; }
        
        /* Filter Panel */
        .filter-panel {
            background: rgba(255, 255, 255, 0.05); border-radius: 12px;
            padding: 20px; margin-bottom: 20px; display: flex; flex-wrap: wrap;
            gap: 15px; align-items: center; justify-content: center;
        }
        .filter-group { display: flex; flex-direction: column; gap: 5px; }
        .filter-group label { font-size: 0.8rem; color: #a0a0a0; text-transform: uppercase; }
        .filter-group select, .filter-group input {
            padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.2);
            background: rgba(0,0,0,0.3); color: #fff; font-size: 0.9rem;
        }
        .filter-group select:focus, .filter-group input:focus {
            outline: none; border-color: #448aff;
        }
        .btn {
            padding: 8px 20px; border-radius: 6px; border: none; cursor: pointer;
            font-size: 0.9rem; font-weight: 600; transition: all 0.2s;
        }
        .btn-primary { background: #448aff; color: #fff; }
        .btn-primary:hover { background: #69a0ff; }
        .btn-secondary { background: rgba(255,255,255,0.1); color: #fff; }
        .btn-secondary:hover { background: rgba(255,255,255,0.2); }
        
        /* Chart Container */
        .chart-container {
            background: rgba(255, 255, 255, 0.05); border-radius: 16px;
            padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        }
        #bubble-chart { width: 100%; height: 500px; }
        .legend-info {
            display: flex; justify-content: center; gap: 30px;
            margin-top: 15px; font-size: 0.9rem; color: #a0a0a0;
        }
        
        /* Table Container */
        .table-container {
            background: rgba(255, 255, 255, 0.05); border-radius: 16px;
            padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
            overflow-x: auto;
        }
        .table-header {
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 15px; flex-wrap: wrap; gap: 10px;
        }
        .table-title { font-size: 1.3rem; font-weight: 600; color: #fff; }
        .table-controls { display: flex; gap: 10px; }
        table { width: 100%; border-collapse: collapse; font-size: 0.9rem; }
        th, td { padding: 12px 15px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.1); }
        th {
            background: rgba(0,0,0,0.3); color: #a0a0a0; font-weight: 600;
            cursor: pointer; user-select: none; white-space: nowrap;
        }
        th:hover { background: rgba(0,0,0,0.5); }
        th.sorted-asc::after { content: ' ▲'; color: #448aff; }
        th.sorted-desc::after { content: ' ▼'; color: #448aff; }
        tr:hover { background: rgba(255,255,255,0.05); }
        .rank-col { width: 50px; text-align: center; color: #6a6a6a; }
        .ticker-col { font-weight: 600; color: #448aff; }
        .positive { color: #00c853; }
        .negative { color: #ff5252; }
        .pagination {
            display: flex; justify-content: center; gap: 10px; margin-top: 15px;
        }
        .page-btn {
            padding: 6px 12px; border-radius: 4px; border: 1px solid rgba(255,255,255,0.2);
            background: rgba(0,0,0,0.3); color: #fff; cursor: pointer;
        }
        .page-btn:hover, .page-btn.active { background: #448aff; border-color: #448aff; }
        
        /* Insights Section */
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
        
        /* Stats Bar */
        .stats-bar {
            display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
            gap: 15px; margin-bottom: 20px;
        }
        .stat-card {
            background: rgba(255,255,255,0.08); border-radius: 10px; padding: 15px;
            text-align: center;
        }
        .stat-label { font-size: 0.75rem; color: #a0a0a0; text-transform: uppercase; margin-bottom: 5px; }
        .stat-value { font-size: 1.3rem; font-weight: 700; color: #fff; }
        
        footer { text-align: center; padding: 30px 20px; margin-top: 20px; color: #6a6a6a; font-size: 0.85rem; }
        
        @media (max-width: 768px) {
            h1 { font-size: 1.8rem; } #bubble-chart { height: 350px; }
            .insights-grid { grid-template-columns: 1fr; } .filter-panel { flex-direction: column; }
            .table-container { overflow-x: scroll; } th, td { padding: 8px 10px; font-size: 0.8rem; }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>S&P 500 Top 100 Companies</h1>
            <p class="subtitle">Interactive Bubble Chart Visualization with Filters & Rankings</p>
            <p class="date-info">Data as of March 2026 | Market Cap, Revenue, Profit & 12-Month Performance</p>
        </header>
        
        <!-- Filter Panel -->
        <div class="filter-panel">
            <div class="filter-group">
                <label>Sort By</label>
                <select id="sortBy">
                    <option value="market_cap">Market Cap</option>
                    <option value="ttm_revenue">Revenue</option>
                    <option value="ttm_net_profit">Net Profit</option>
                    <option value="price_change_12m">12M Change %</option>
                    <option value="profit_margin">Profit Margin %</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Order</label>
                <select id="sortOrder">
                    <option value="desc">Descending ▼</option>
                    <option value="asc">Ascending ▲</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Min Market Cap</label>
                <select id="minMarketCap">
                    <option value="0">All</option>
                    <option value="100000000000">$100B+</option>
                    <option value="250000000000">$250B+</option>
                    <option value="500000000000">$500B+</option>
                    <option value="1000000000000">$1T+</option>
                </select>
            </div>
            <div class="filter-group">
                <label>Performance</label>
                <select id="performance">
                    <option value="all">All</option>
                    <option value="positive">Positive Only</option>
                    <option value="negative">Negative Only</option>
                </select>
            </div>
            <div class="filter-group" style="justify-content: flex-end;">
                <label>&nbsp;</label>
                <button class="btn btn-primary" onclick="applyFilters()">Apply Filters</button>
            </div>
            <div class="filter-group" style="justify-content: flex-end;">
                <label>&nbsp;</label>
                <button class="btn btn-secondary" onclick="resetFilters()">Reset</button>
            </div>
        </div>
        
        <!-- Stats Bar -->
        <div class="stats-bar" id="statsBar"></div>
        
        <!-- Chart Container -->
        <div class="chart-container">
            <div id="bubble-chart"></div>
            <div class="legend-info">
                <div class="legend-item">
                    <span style="font-size: 0.85em;">💡 Bubble Size = Market Cap | Color = 12M Price Change</span>
                </div>
            </div>
        </div>
        
        <!-- Ranking Table -->
        <div class="table-container">
            <div class="table-header">
                <div class="table-title">📊 Company Rankings</div>
                <div class="table-controls">
                    <input type="text" id="searchBox" placeholder="🔍 Search ticker or name..." 
                           style="padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(255,255,255,0.2); 
                                  background: rgba(0,0,0,0.3); color: #fff; font-size: 0.9rem;"
                           onkeyup="filterTable()">
                </div>
            </div>
            <table id="rankingTable">
                <thead>
                    <tr>
                        <th class="rank-col">#</th>
                        <th data-sort="ticker">Ticker</th>
                        <th data-sort="name">Company</th>
                        <th data-sort="market_cap" style="text-align: right;">Market Cap</th>
                        <th data-sort="ttm_revenue" style="text-align: right;">Revenue (TTM)</th>
                        <th data-sort="ttm_net_profit" style="text-align: right;">Net Profit (TTM)</th>
                        <th data-sort="profit_margin" style="text-align: right;">Margin %</th>
                        <th data-sort="price_change_12m" style="text-align: right;">12M Change</th>
                    </tr>
                </thead>
                <tbody id="tableBody"></tbody>
            </table>
            <div class="pagination" id="pagination"></div>
        </div>
        
        <!-- Insights Section -->
        <div class="insights-section">
            <div class="insights-header"><h2>🔍 Key Findings</h2></div>
            <div class="insights-grid" id="insights-grid"></div>
        </div>
        
        <footer>
            <p>Data sourced from public financial reports | Visualization generated March 2026</p>
        </footer>
    </div>
    
    <script>
        const ALL_COMPANIES = COMPANIES_DATA;
        let filteredCompanies = [...ALL_COMPANIES];
        let currentSort = { field: 'market_cap', order: 'desc' };
        let currentPage = 1;
        const rowsPerPage = 20;
        
        // Calculate profit margin for all companies
        ALL_COMPANIES.forEach(c => {
            c.profit_margin = c.ttm_revenue > 0 ? (c.ttm_net_profit / c.ttm_revenue * 100) : 0;
        });
        
        function formatBillions(v) { return (v / 1e9).toFixed(1) + 'B'; }
        function formatTrillions(v) { return (v / 1e12).toFixed(2) + 'T'; }
        function formatPercent(v) { return (v > 0 ? '+' : '') + v.toFixed(1) + '%'; }
        
        function applyFilters() {
            const sortBy = document.getElementById('sortBy').value;
            const sortOrder = document.getElementById('sortOrder').value;
            const minMarketCap = parseFloat(document.getElementById('minMarketCap').value);
            const performance = document.getElementById('performance').value;
            
            filteredCompanies = ALL_COMPANIES.filter(c => {
                if (c.market_cap < minMarketCap) return false;
                if (performance === 'positive' && c.price_change_12m <= 0) return false;
                if (performance === 'negative' && c.price_change_12m >= 0) return false;
                return true;
            });
            
            currentSort = { field: sortBy, order: sortOrder };
            filteredCompanies.sort((a, b) => {
                let valA = a[sortBy] || 0;
                let valB = b[sortBy] || 0;
                return sortOrder === 'desc' ? valB - valA : valA - valB;
            });
            
            currentPage = 1;
            updateStats();
            renderChart();
            renderTable();
            renderInsights();
        }
        
        function resetFilters() {
            document.getElementById('sortBy').value = 'market_cap';
            document.getElementById('sortOrder').value = 'desc';
            document.getElementById('minMarketCap').value = '0';
            document.getElementById('performance').value = 'all';
            document.getElementById('searchBox').value = '';
            applyFilters();
        }
        
        function filterTable() {
            renderTable();
        }
        
        function updateStats() {
            const totalMarketCap = filteredCompanies.reduce((sum, c) => sum + c.market_cap, 0);
            const totalRevenue = filteredCompanies.reduce((sum, c) => sum + c.ttm_revenue, 0);
            const totalProfit = filteredCompanies.reduce((sum, c) => sum + c.ttm_net_profit, 0);
            const avgMargin = filteredCompanies.reduce((sum, c) => sum + c.profit_margin, 0) / filteredCompanies.length;
            const positiveCount = filteredCompanies.filter(c => c.price_change_12m > 0).length;
            
            const statsBar = document.getElementById('statsBar');
            statsBar.innerHTML = `
                <div class="stat-card">
                    <div class="stat-label">Companies</div>
                    <div class="stat-value">${filteredCompanies.length}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Market Cap</div>
                    <div class="stat-value">$${formatTrillions(totalMarketCap)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Revenue</div>
                    <div class="stat-value">$${formatTrillions(totalRevenue)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Total Net Profit</div>
                    <div class="stat-value">$${formatTrillions(totalProfit)}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Avg Profit Margin</div>
                    <div class="stat-value">${avgMargin.toFixed(1)}%</div>
                </div>
                <div class="stat-card">
                    <div class="stat-label">Positive Performers</div>
                    <div class="stat-value positive">${positiveCount}/${filteredCompanies.length}</div>
                </div>
            `;
        }
        
        function renderChart() {
            const xValues = filteredCompanies.map(c => c.ttm_revenue / 1e9);
            const yValues = filteredCompanies.map(c => c.ttm_net_profit / 1e9);
            const sizes = filteredCompanies.map(c => Math.log10(c.market_cap / 1e9) * 8);
            const priceChanges = filteredCompanies.map(c => c.price_change_12m);
            
            const trace = {
                x: xValues, y: yValues, mode: 'markers+text', type: 'scatter',
                text: filteredCompanies.map(c => c.ticker), textposition: 'top center',
                textfont: {color: '#fff', size: 10, family: 'monospace'},
                hovertemplate: '<b>%{text}</b><br>%{customdata.name}<br><br>Revenue: $%{customdata.revenue}B<br>Net Profit: $%{customdata.profit}B<br>Market Cap: $%{customdata.mcap}T<br>12M Change: %{customdata.change}%<extra></extra>',
                customdata: filteredCompanies.map(c => ({
                    name: c.name, revenue: (c.ttm_revenue / 1e9).toFixed(1),
                    profit: (c.ttm_net_profit / 1e9).toFixed(1),
                    mcap: (c.market_cap / 1e12).toFixed(2),
                    change: formatPercent(c.price_change_12m)
                })),
                marker: {
                    size: sizes, color: priceChanges,
                    colorscale: [[-1, '#ff1744'], [-0.5, '#ff5252'], [-0.25, '#ff8a80'], [0, '#ffffff'], [0.25, '#a5d6a7'], [0.5, '#66bb6a'], [1, '#00c853']],
                    colorbar: { title: '12M Change %', titleside: 'right', titlefont: {color: '#a0a0a0', size: 12}, tickfont: {color: '#a0a0a0'}, len: 0.6, thickness: 20 },
                    line: { color: 'rgba(255, 255, 255, 0.5)', width: 1.5 }, sizemode: 'diameter', sizemin: 8, sizeref: 0.5
                }
            };
            
            const layout = {
                title: { text: 'TTM Revenue vs Net Profit (Bubble Size = Market Cap)', font: {color: '#fff', size: 16} },
                xaxis: { title: {text: 'TTM Revenue ($ Billions)', font: {color: '#a0a0a0'}}, type: 'log', gridcolor: 'rgba(255, 255, 255, 0.1)', tickfont: {color: '#a0a0a0'} },
                yaxis: { title: {text: 'TTM Net Profit ($ Billions)', font: {color: '#a0a0a0'}}, gridcolor: 'rgba(255, 255, 255, 0.1)', tickfont: {color: '#a0a0a0'} },
                paper_bgcolor: 'rgba(0,0,0,0)', plot_bgcolor: 'rgba(0,0,0,0)', hovermode: 'closest', margin: {l: 80, r: 100, t: 50, b: 60}
            };
            Plotly.newPlot('bubble-chart', [trace], layout, {responsive: true});
        }
        
        function renderTable() {
            const search = document.getElementById('searchBox').value.toLowerCase();
            const filtered = filteredCompanies.filter(c => 
                c.ticker.toLowerCase().includes(search) || c.name.toLowerCase().includes(search)
            );
            
            const tbody = document.getElementById('tableBody');
            const start = (currentPage - 1) * rowsPerPage;
            const end = start + rowsPerPage;
            const pageData = filtered.slice(start, end);
            
            tbody.innerHTML = pageData.map((c, i) => `
                <tr>
                    <td class="rank-col">${start + i + 1}</td>
                    <td class="ticker-col">${c.ticker}</td>
                    <td>${c.name}</td>
                    <td style="text-align: right;">$${formatTrillions(c.market_cap)}</td>
                    <td style="text-align: right;">$${formatBillions(c.ttm_revenue)}</td>
                    <td style="text-align: right;">$${formatBillions(c.ttm_net_profit)}</td>
                    <td style="text-align: right;" class="${c.profit_margin >= 0 ? 'positive' : 'negative'}">${c.profit_margin.toFixed(1)}%</td>
                    <td style="text-align: right;" class="${c.price_change_12m >= 0 ? 'positive' : 'negative'}">${formatPercent(c.price_change_12m)}</td>
                </tr>
            `).join('');
            
            // Pagination
            const totalPages = Math.ceil(filtered.length / rowsPerPage);
            const pagination = document.getElementById('pagination');
            if (totalPages > 1) {
                let html = '';
                for (let i = 1; i <= totalPages; i++) {
                    html += `<button class="page-btn ${i === currentPage ? 'active' : ''}" onclick="goToPage(${i})">${i}</button>`;
                }
                pagination.innerHTML = html;
            } else {
                pagination.innerHTML = '';
            }
        }
        
        function goToPage(page) {
            currentPage = page;
            renderTable();
        }
        
        function renderInsights() {
            const topByCap = [...filteredCompanies].sort((a, b) => b.market_cap - a.market_cap)[0];
            const topByRevenue = [...filteredCompanies].sort((a, b) => b.ttm_revenue - a.ttm_revenue)[0];
            const topByProfit = [...filteredCompanies].sort((a, b) => b.ttm_net_profit - a.ttm_net_profit)[0];
            const topByMargin = [...filteredCompanies].sort((a, b) => b.profit_margin - a.profit_margin)[0];
            const bestPerformer = [...filteredCompanies].sort((a, b) => b.price_change_12m - a.price_change_12m)[0];
            const worstPerformer = [...filteredCompanies].sort((a, b) => a.price_change_12m - b.price_change_12m)[0];
            
            const totalMarketCap = filteredCompanies.reduce((sum, c) => sum + c.market_cap, 0);
            const avgMargin = filteredCompanies.reduce((sum, c) => sum + c.profit_margin, 0) / filteredCompanies.length;
            const positiveCount = filteredCompanies.filter(c => c.price_change_12m > 0).length;
            
            const insights = [
                {
                    id: 1, title: "Highest Market Cap", type: "highlight",
                    value: `$${formatTrillions(topByCap.market_cap)}`,
                    company: topByCap.name, ticker: topByCap.ticker,
                    detail: `Largest company in filtered set`
                },
                {
                    id: 2, title: "Highest Profit Margin", type: "positive",
                    value: `${topByMargin.profit_margin.toFixed(1)}%`,
                    company: topByMargin.name, ticker: topByMargin.ticker,
                    detail: `Most efficient at converting revenue to profit`
                },
                {
                    id: 3, title: "Top Revenue Generator", type: "neutral",
                    value: `$${formatBillions(topByRevenue.ttm_revenue)}`,
                    company: topByRevenue.name, ticker: topByRevenue.ticker,
                    detail: `Highest TTM revenue`
                },
                {
                    id: 4, title: "Most Profitable", type: "positive",
                    value: `$${formatBillions(topByProfit.ttm_net_profit)}`,
                    company: topByProfit.name, ticker: topByProfit.ticker,
                    detail: `Highest TTM net profit`
                },
                {
                    id: 5, title: "Best 12M Performer", type: "positive",
                    value: formatPercent(bestPerformer.price_change_12m),
                    company: bestPerformer.name, ticker: bestPerformer.ticker,
                    detail: `Top stock performance over 12 months`
                },
                {
                    id: 6, title: "Worst 12M Performer", type: "negative",
                    value: formatPercent(worstPerformer.price_change_12m),
                    company: worstPerformer.name, ticker: worstPerformer.ticker,
                    detail: `Lowest stock performance over 12 months`
                },
                {
                    id: 7, title: "Average Profit Margin", type: "neutral",
                    value: `${avgMargin.toFixed(1)}%`,
                    detail: `Across ${filteredCompanies.length} companies`
                },
                {
                    id: 8, title: "Total Market Value", type: "highlight",
                    value: `$${formatTrillions(totalMarketCap)}`,
                    detail: `Combined market cap of filtered companies`
                },
                {
                    id: 9, title: "Positive Performers", type: "positive",
                    value: `${positiveCount} / ${filteredCompanies.length}`,
                    detail: `${((positiveCount/filteredCompanies.length)*100).toFixed(0)}% with positive 12M returns`
                },
                {
                    id: 10, title: "Revenue vs Market Cap Outlier", type: "neutral",
                    high: { company: [...filteredCompanies].sort((a,b) => (b.ttm_revenue/b.market_cap) - (a.ttm_revenue/a.market_cap))[0]?.name || 'N/A', 
                            ticker: [...filteredCompanies].sort((a,b) => (b.ttm_revenue/b.market_cap) - (a.ttm_revenue/a.market_cap))[0]?.ticker || 'N/A',
                            ratio: 'High Rev/MCap' },
                    low: { company: topByCap.name, ticker: topByCap.ticker, ratio: 'Low Rev/MCap' },
                    detail: `Revenue-to-Market Cap ratio analysis`
                }
            ];
            
            const grid = document.getElementById('insights-grid');
            grid.innerHTML = insights.map(insight => {
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
                if (insight.high && insight.low) {
                    content += `<div class="outlier-container">
                        <div class="outlier-box"><div class="outlier-label">High Ratio</div><div class="outlier-company">${insight.high.company} (${insight.high.ticker})</div><div class="outlier-ratio">${insight.high.ratio}</div></div>
                        <div class="outlier-box"><div class="outlier-label">Low Ratio</div><div class="outlier-company">${insight.low.company} (${insight.low.ticker})</div><div class="outlier-ratio">${insight.low.ratio}</div></div>
                    </div>`;
                }
                content += `<div class="insight-detail">${insight.detail}</div>`;
                return `<div class="insight-card ${insight.type}">${content}</div>`;
            }).join('');
        }
        
        // Table column sorting
        document.querySelectorAll('th[data-sort]').forEach(th => {
            th.addEventListener('click', () => {
                const field = th.dataset.sort;
                document.getElementById('sortBy').value = field;
                applyFilters();
            });
        });
        
        // Initialize
        document.addEventListener('DOMContentLoaded', () => {
            applyFilters();
        });
    </script>
</body>
</html>
'''

# Replace placeholders
html = html.replace('COMPANIES_DATA', json.dumps(companies, indent=8))

with open('index.html', 'w') as f:
    f.write(html)

print(f"✅ Built enhanced index.html with {len(companies)} companies, filters, table, and dynamic insights")
