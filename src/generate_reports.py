import os
import json

def generate_reports():
    # Load the data
    with open("data/report_data.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        
    summary = data["catalog_summary"]
    cats = data["category_stats"]
    brands = data["brand_stats"]
    demographics = data["demographics"]
    trends = data["yearly_reviews"]
    helpfulness = data["helpfulness_by_rating"]
    nlp = data["nlp_stats"]
    vader = data["vader_by_rating"]
    insights = data["business_insights"]
    
    # -------------------------------------------------------------------------
    # GENERATE MARKDOWN REPORT
    # -------------------------------------------------------------------------
    md_content = f"""# Sephora E-Commerce Portfolio Analytics Report
*An Executive-Ready Data Science, NLP & Business Intelligence Analysis*

---

## 1. Executive Summary

This report presents a high-rigor, data-driven analysis of the Sephora e-commerce ecosystem, analyzing a dataset of **{summary["total_products"]:,} products** and **{summary["total_reviews"]:,} customer reviews** representing **{summary["total_loves"]:,} user loves (likes)**. 

### Key High-Level Metrics
* **Total Products**: {summary["total_products"]:,}
* **Total Reviews Count**: {summary["total_reviews"]:,}
* **Total Customer Loves (Likes)**: {summary["total_loves"]:,}
* **Average Catalog Price**: ${summary["avg_price"]:.2f}
* **Median Catalog Price**: ${summary["median_price"]:.2f}
* **Price Range**: ${summary["min_price"]:.2f} to ${summary["max_price"]:.2f}

---

## 2. Product Catalog & Inventory Profile

### Category Breakdown
The Sephora catalog is dominated by **Skincare** (28.5%) and **Makeup** (27.9%), followed by Hair Care (17.2%) and Fragrance (16.9%). 

| Primary Category | Product Count | Percentage | Average Price | Median Price | Average Rating |
| :--- | :---: | :---: | :---: | :---: | :---: |
"""
    for cat in cats:
        md_content += f"| {cat['category']} | {cat['count']:,} | {cat['pct']:.2f}% | ${cat['avg_price']:.2f} | ${cat['median_price']:.2f} | {cat['avg_rating']:.2f} ★ |\n"
        
    md_content += """
### Price Distributions and Brand Presence
Fragrances command the highest average price ($87.26), while Skincare exhibits a right-skewed price distribution stretching up to luxury products. The top brand by catalog volume is **SEPHORA COLLECTION** (352 products), offering the lowest average price of $16.38, serving as a budget entry point for consumers.

![Category Distribution](figures/category_distribution.png)
![Price by Category](figures/price_by_category.png)

---

## 3. Customer Demographics & Historical Trends

### Reviewer Profile Segmentation
Understanding customer demographics is critical for targeting. Our analysis shows that:
* **Skin Types**: **Combination skin** is the dominant reviewer profile, representing **49.75%** of all reviews, followed by Dry skin (16.99%), Normal skin (12.05%), and Oily skin (11.01%).
* **Skin Tones**: **Light** (24.34%), **Fair** (19.01%), and **LightMedium** (17.96%) tones are the most frequently reported profiles.

### Reviews Volume Trend
The reviews volume has grown exponentially, peaking in **2020** (215,449 reviews) and **2021** (202,012 reviews) before stabilizing, showing strong holiday seasonal spikes (Nov-Dec).

![Reviewer Demographic Profiles](figures/reviewer_profiles.png)
![Reviews Volume Over Time](figures/reviews_over_time.png)

---

## 4. NLP & Sentiment Analysis

### Customer Text Mining
Review text mining reveals distinct lexicons between highly-satisfied and highly-dissatisfied customers:
* **Positive Review Keywords (5-Star)**: Focus on product efficacy and sensory rewards (`love`, `use`, `skin`, `great`, `feel`, `dry`).
* **Negative Review Keywords (1-Star)**: Emphasize disappointment and failures (`skin`, `like`, `just`, `dry`, `using`, `didnt`, `dont`).

### Sentiment & Rating Efficacy (VADER)
The average VADER compound sentiment score exhibits a strong monotonic relationship with star ratings:
* **1-Star**: {vader["1"]:.3f} (Near neutral/conflicted)
* **2-Star**: {vader["2"]:.3f}
* **3-Star**: {vader["3"]:.3f}
* **4-Star**: {vader["4"]:.3f}
* **5-Star**: {vader["5"]:.3f} (Highly positive)

This correlation validates that customer text-level sentiment aligns strongly with their rating scores.

![Sentiment vs Rating](figures/sentiment_vs_rating.png)

---

## 5. Strategic Business Metrics & Product Insights

We engineered custom indices to identify highly-actionable product segments.

### A. Value for Money Products
Using the formula $\\text{Value Index} = \\frac{\\text{Rating} \\times \\ln(\\text{Loves Count} + 1)}{\\text{Price (USD)}}$, we identify budget-friendly items that generate maximum engagement and customer satisfaction. The top performers are:

| Product Name | Brand | Price | Rating | Loves | Value Index |
| :--- | :--- | :---: | :---: | :---: | :---: |
"""
    for p in insights["value_for_money"]:
        md_content += f"| {p['product_name']} | {p['brand_name']} | ${p['price_usd']:.2f} | {p['rating']:.2f} ★ | {p['loves_count']:,} | {p['value_index']:.2f} |\n"
        
    md_content += """
*Insight*: **SEPHORA COLLECTION** and **The Ordinary** dominate this list, representing exceptional customer value.

### B. Hidden Gems
These are products with ratings $\\ge 4.5$ but between 10 and 50 reviews, sorted by Loves. They represent high-quality products with strong user loyalty that have not yet gone mainstream.

| Product Name | Brand | Price | Rating | Loves | Reviews |
| :--- | :--- | :---: | :---: | :---: | :---: |
"""
    for p in insights["hidden_gems"]:
        md_content += f"| {p['product_name']} | {p['brand_name']} | ${p['price_usd']:.2f} | {p['rating']:.2f} ★ | {p['loves_count']:,} | {p['reviews']} |\n"
        
    md_content += """
*Insight*: **Rare Beauty** and **Fenty Beauty** are generating under-marketed gems (e.g. Rare Beauty Blush Brush and Fenty Lip Gloss Trio). Pushing these via marketing campaigns could yield high ROI.

### C. Overrated Luxury Products
These are premium products priced $\\ge \\$80$ with customer ratings $\\le 3.5$ and at least 30 reviews. They represent customer friction points where the luxury price tag fails to meet product quality.

| Product Name | Brand | Price | Rating | Loves | Reviews |
| :--- | :--- | :---: | :---: | :---: | :---: |
"""
    for p in insights["overrated"]:
        md_content += f"| {p['product_name']} | {p['brand_name']} | ${p['price_usd']:.2f} | {p['rating']:.2f} ★ | {p['loves_count']:,} | {p['reviews']} |\n"
        
    md_content += """
*Insight*: Ultra-premium items like **Dr. Barbara Sturm Sun Drops ($150, 2.72★)** and **FOREO LUNA fofo ($89, 2.89★)** represent major customer complaints. These brands should be flagged for R&D reformulation or margin adjustments.

![Value for Money Products](figures/value_for_money.png)
![Hidden Gems](figures/hidden_gems.png)
![Overrated Products](figures/overrated_products.png)

---
*Report generated programmatically from Sephora E-Commerce EDA Pipeline.*
"""
    
    with open("reports/beauty_product_analytics_report.md", "w", encoding="utf-8") as f:
        f.write(md_content)
    print("Saved Markdown report: reports/beauty_product_analytics_report.md")
    
    # -------------------------------------------------------------------------
    # GENERATE HTML REPORT (PREMIUM INTERACTIVE DASHBOARD)
    # -------------------------------------------------------------------------
    
    # Format category rows
    cat_rows_html = ""
    for cat in cats:
        cat_rows_html += f"""
        <tr>
            <td><strong>{cat['category']}</strong></td>
            <td>{cat['count']:,}</td>
            <td>{cat['pct']:.2f}%</td>
            <td>${cat['avg_price']:.2f}</td>
            <td>${cat['median_price']:.2f}</td>
            <td><span class="rating-badge">{cat['avg_rating']:.2f} ★</span></td>
        </tr>
        """
        
    # Format value for money rows
    vfm_rows_html = ""
    for p in insights["value_for_money"]:
        vfm_rows_html += f"""
        <tr>
            <td><strong>{p['product_name']}</strong></td>
            <td>{p['brand_name']}</td>
            <td>${p['price_usd']:.2f}</td>
            <td><span class="rating-badge">{p['rating']:.2f} ★</span></td>
            <td>{p['loves_count']:,}</td>
            <td><span class="index-badge">{p['value_index']:.2f}</span></td>
        </tr>
        """
        
    # Format hidden gems rows
    gems_rows_html = ""
    for p in insights["hidden_gems"]:
        gems_rows_html += f"""
        <tr>
            <td><strong>{p['product_name']}</strong></td>
            <td>{p['brand_name']}</td>
            <td>${p['price_usd']:.2f}</td>
            <td><span class="rating-badge">{p['rating']:.2f} ★</span></td>
            <td>{p['loves_count']:,}</td>
            <td>{p['reviews']}</td>
        </tr>
        """
        
    # Format overrated rows
    overrated_rows_html = ""
    for p in insights["overrated"]:
        overrated_rows_html += f"""
        <tr>
            <td><strong>{p['product_name']}</strong></td>
            <td>{p['brand_name']}</td>
            <td class="text-danger">${p['price_usd']:.2f}</td>
            <td><span class="rating-badge bad">{p['rating']:.2f} ★</span></td>
            <td>{p['loves_count']:,}</td>
            <td>{p['reviews']}</td>
        </tr>
        """
        
    # Format skin type items
    skin_type_html = ""
    for st, val in demographics["skin_types"].items():
        skin_type_html += f"""
        <div class="demographic-card">
            <span class="demo-label">{st.capitalize()}</span>
            <span class="demo-value">{val:.1f}%</span>
            <div class="demo-bar-container"><div class="demo-bar" style="width: {val}%"></div></div>
        </div>
        """
        
    # Format skin tone items
    skin_tone_html = ""
    for st, val in demographics["skin_tones"].items():
        skin_tone_html += f"""
        <div class="demographic-card">
            <span class="demo-label">{st.capitalize()}</span>
            <span class="demo-value">{val:.1f}%</span>
            <div class="demo-bar-container"><div class="demo-bar" style="width: {val}%"></div></div>
        </div>
        """

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Sephora E-Commerce Performance Dashboard</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #0A0A0A;
            --card-bg: #141414;
            --border-color: #222222;
            --text-color: #E0E0E0;
            --text-muted: #888888;
            --primary-color: #FF3366;
            --primary-glow: rgba(255, 51, 102, 0.15);
            --secondary-color: #3498DB;
            --success-color: #2ECC71;
            --warning-color: #F1C40F;
            --danger-color: #E74C3C;
            --font-display: 'Outfit', sans-serif;
            --font-body: 'Inter', sans-serif;
        }}

        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}

        body {{
            background-color: var(--bg-color);
            color: var(--text-color);
            font-family: var(--font-body);
            line-height: 1.6;
            padding-bottom: 60px;
        }}

        header {{
            background: linear-gradient(180deg, rgba(26,26,26,0.8) 0%, rgba(10,10,10,0.8) 100%);
            border-bottom: 1px solid var(--border-color);
            padding: 20px 5%;
            position: sticky;
            top: 0;
            z-index: 100;
            backdrop-filter: blur(10px);
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}

        .brand-logo {{
            font-family: var(--font-display);
            font-size: 24px;
            font-weight: 800;
            background: linear-gradient(90deg, #FFFFFF 0%, var(--primary-color) 100%);
            -webkit-background-clip: text;
            background-clip: text;
            -webkit-text-fill-color: transparent;
            display: flex;
            align-items: center;
            gap: 10px;
        }}

        .brand-logo::before {{
            content: '';
            display: inline-block;
            width: 14px;
            height: 14px;
            background-color: var(--primary-color);
            border-radius: 50%;
            box-shadow: 0 0 10px var(--primary-color);
        }}

        .report-meta {{
            font-size: 13px;
            color: var(--text-muted);
            background-color: var(--card-bg);
            padding: 6px 12px;
            border-radius: 20px;
            border: 1px solid var(--border-color);
        }}

        main {{
            max-width: 1300px;
            margin: 40px auto;
            padding: 0 20px;
        }}

        .hero-banner {{
            margin-bottom: 40px;
            border-radius: 16px;
            overflow: hidden;
            border: 1px solid var(--border-color);
            position: relative;
            box-shadow: 0 20px 40px rgba(0,0,0,0.5);
        }}

        .hero-banner img {{
            width: 100%;
            display: block;
            max-height: 250px;
            object-fit: cover;
            opacity: 0.85;
        }}

        /* KPI Dashboard */
        .kpi-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
            gap: 20px;
            margin-bottom: 40px;
        }}

        .kpi-card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 24px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            transition: transform 0.3s ease, border-color 0.3s ease, box-shadow 0.3s ease;
        }}

        .kpi-card:hover {{
            transform: translateY(-4px);
            border-color: var(--primary-color);
            box-shadow: 0 10px 20px rgba(255, 51, 102, 0.05);
        }}

        .kpi-label {{
            font-size: 13px;
            color: var(--text-muted);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 8px;
        }}

        .kpi-value {{
            font-family: var(--font-display);
            font-size: 32px;
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 8px;
        }}

        .kpi-note {{
            font-size: 12px;
            color: var(--primary-color);
            display: flex;
            align-items: center;
            gap: 4px;
        }}

        /* Navigation Tabs */
        .nav-tabs {{
            display: flex;
            border-bottom: 1px solid var(--border-color);
            margin-bottom: 30px;
            gap: 10px;
            overflow-x: auto;
            padding-bottom: 1px;
        }}

        .tab-btn {{
            background: none;
            border: none;
            color: var(--text-muted);
            padding: 12px 24px;
            font-family: var(--font-display);
            font-size: 15px;
            font-weight: 600;
            cursor: pointer;
            border-radius: 8px 8px 0 0;
            border-bottom: 2px solid transparent;
            transition: all 0.3s ease;
            white-space: nowrap;
        }}

        .tab-btn:hover {{
            color: #FFFFFF;
            background-color: rgba(255,255,255,0.02);
        }}

        .tab-btn.active {{
            color: var(--primary-color);
            border-bottom-color: var(--primary-color);
            background-color: var(--primary-glow);
        }}

        /* Tab Content Panel */
        .tab-panel {{
            display: none;
            animation: fadeIn 0.4s ease;
        }}

        .tab-panel.active {{
            display: block;
        }}

        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(10px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}

        /* Section Layouts */
        .section-grid {{
            display: grid;
            grid-template-columns: 1.2fr 0.8fr;
            gap: 30px;
            margin-bottom: 30px;
        }}

        @media (max-width: 1024px) {{
            .section-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .card {{
            background-color: var(--card-bg);
            border: 1px solid var(--border-color);
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 30px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }}

        .card-title {{
            font-family: var(--font-display);
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 20px;
            color: #FFFFFF;
            display: flex;
            align-items: center;
            justify-content: space-between;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 12px;
        }}

        .card-description {{
            font-size: 14px;
            color: var(--text-muted);
            margin-bottom: 20px;
        }}

        /* Table Styling */
        .table-responsive {{
            overflow-x: auto;
            width: 100%;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            text-align: left;
            font-size: 14px;
        }}

        th {{
            background-color: rgba(255,255,255,0.02);
            color: #FFFFFF;
            font-weight: 600;
            padding: 12px 16px;
            border-bottom: 1px solid var(--border-color);
            font-family: var(--font-display);
            text-transform: uppercase;
            font-size: 12px;
            letter-spacing: 0.5px;
        }}

        td {{
            padding: 14px 16px;
            border-bottom: 1px solid rgba(255,255,255,0.05);
            color: var(--text-color);
        }}

        tr:hover td {{
            background-color: rgba(255,255,255,0.01);
            color: #FFFFFF;
        }}

        .rating-badge {{
            background-color: var(--primary-glow);
            color: var(--primary-color);
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 12px;
            border: 1px solid rgba(255, 51, 102, 0.3);
        }}

        .rating-badge.bad {{
            background-color: rgba(231, 76, 60, 0.1);
            color: var(--danger-color);
            border: 1px solid rgba(231, 76, 60, 0.3);
        }}

        .index-badge {{
            background-color: rgba(46, 204, 113, 0.15);
            color: var(--success-color);
            padding: 4px 8px;
            border-radius: 4px;
            font-weight: 600;
            font-size: 12px;
            border: 1px solid rgba(46, 204, 113, 0.3);
        }}

        .text-danger {{
            color: var(--danger-color);
            font-weight: 600;
        }}

        /* Plot Image Wrapper */
        .plot-container {{
            border: 1px solid var(--border-color);
            border-radius: 12px;
            overflow: hidden;
            background-color: #FFFFFF; /* Matplotlib charts usually look best on white background */
            padding: 10px;
            display: flex;
            justify-content: center;
            align-items: center;
            box-shadow: inset 0 0 10px rgba(0,0,0,0.05);
            transition: border-color 0.3s ease;
        }}

        .plot-container:hover {{
            border-color: var(--primary-color);
        }}

        .plot-container img {{
            max-width: 100%;
            height: auto;
            border-radius: 6px;
        }}

        /* Demographics container */
        .demographics-container {{
            display: flex;
            flex-direction: column;
            gap: 15px;
        }}

        .demographic-card {{
            background-color: rgba(255,255,255,0.02);
            border: 1px solid var(--border-color);
            border-radius: 8px;
            padding: 12px 16px;
            display: flex;
            flex-direction: column;
            gap: 6px;
        }}

        .demo-label {{
            font-size: 13px;
            color: #FFFFFF;
            font-weight: 600;
        }}

        .demo-value {{
            font-size: 20px;
            font-family: var(--font-display);
            font-weight: 700;
            color: var(--primary-color);
        }}

        .demo-bar-container {{
            width: 100%;
            height: 6px;
            background-color: rgba(255,255,255,0.05);
            border-radius: 3px;
            overflow: hidden;
        }}

        .demo-bar {{
            height: 100%;
            background: linear-gradient(90deg, var(--secondary-color) 0%, var(--primary-color) 100%);
            border-radius: 3px;
        }}

        /* Double Figure Grid */
        .plot-row-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }}

        @media (max-width: 768px) {{
            .plot-row-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        /* Business Insights Section */
        .insight-highlight-grid {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}

        @media (max-width: 900px) {{
            .insight-highlight-grid {{
                grid-template-columns: 1fr;
            }}
        }}

        .insight-summary-card {{
            background-color: rgba(255,255,255,0.01);
            border: 1px solid var(--border-color);
            border-radius: 12px;
            padding: 20px;
            border-left: 4px solid var(--primary-color);
        }}

        .insight-summary-card.green {{
            border-left-color: var(--success-color);
        }}

        .insight-summary-card.yellow {{
            border-left-color: var(--warning-color);
        }}

        .insight-summary-card.red {{
            border-left-color: var(--danger-color);
        }}

        .insight-summary-title {{
            font-family: var(--font-display);
            font-size: 16px;
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 8px;
        }}

        .insight-summary-desc {{
            font-size: 13px;
            color: var(--text-muted);
        }}

        /* Business Insight Box Styles */
        .insight-box {{
            background-color: rgba(255,255,255,0.02);
            border: 1px dashed var(--border-color);
            border-left: 4px solid var(--primary-color);
            border-radius: 8px;
            padding: 16px;
            margin-top: 20px;
            font-size: 13.5px;
            color: var(--text-color);
            line-height: 1.5;
        }}
        .insight-box-title {{
            font-family: var(--font-display);
            font-weight: 700;
            color: #FFFFFF;
            margin-bottom: 6px;
            display: flex;
            align-items: center;
            gap: 8px;
            font-size: 14.5px;
        }}
        .insight-box-title::before {{
            content: '💡';
        }}
        .insight-box.success {{
            border-left-color: var(--success-color);
        }}
        .insight-box.warning {{
            border-left-color: var(--warning-color);
        }}
        .insight-box.danger {{
            border-left-color: var(--danger-color);
        }}

    </style>
</head>
<body>

    <header>
        <div class="brand-logo">SEPHORA ANALYTICS</div>
        <div class="report-meta">Data Engine v1.0.0 &bull; Executed Successfully</div>
    </header>

    <main>
        
        <!-- KPI Dashboard Panel -->
        <section class="kpi-grid">
            <div class="kpi-card">
                <div>
                    <div class="kpi-label">Catalog Products</div>
                    <div class="kpi-value">{summary["total_products"]:,}</div>
                </div>
                <div class="kpi-note">Active Inventory Items</div>
            </div>
            <div class="kpi-card">
                <div>
                    <div class="kpi-label">Total Reviews</div>
                    <div class="kpi-value">{summary["total_reviews"]:,}</div>
                </div>
                <div class="kpi-note">1.09M Unique Customers</div>
            </div>
            <div class="kpi-card">
                <div>
                    <div class="kpi-label">Social Loves</div>
                    <div class="kpi-value">247.8M</div>
                </div>
                <div class="kpi-note">Customer Likes & Engagement</div>
            </div>
            <div class="kpi-card">
                <div>
                    <div class="kpi-label">Median Price</div>
                    <div class="kpi-value">${summary["median_price"]:.2f}</div>
                </div>
                <div class="kpi-note">Average: ${summary["avg_price"]:.2f}</div>
            </div>
        </section>

        <!-- Navigation Tabs -->
        <nav class="nav-tabs">
            <button class="tab-btn active" onclick="switchTab('catalog')">1. Catalog & Inventory</button>
            <button class="tab-btn" onclick="switchTab('demographics')">2. Demographics & Trends</button>
            <button class="tab-btn" onclick="switchTab('nlp')">3. NLP & Text Mining</button>
            <button class="tab-btn" onclick="switchTab('business')">4. Strategic Insights</button>
        </nav>

        <!-- 1. Catalog & Inventory Panel -->
        <div id="tab-catalog" class="tab-panel active">
            <div class="section-grid">
                <div class="card">
                    <div class="card-title">Inventory breakdown by Category</div>
                    <div class="card-description">Summary statistics of products, catalog share, and pricing distributions by primary category.</div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>Primary Category</th>
                                    <th>Product Count</th>
                                    <th>Catalog Share</th>
                                    <th>Average Price</th>
                                    <th>Median Price</th>
                                    <th>Avg Rating</th>
                                </tr>
                            </thead>
                            <tbody>
                                {cat_rows_html}
                            </tbody>
                        </table>
                    </div>
                    <div class="insight-box">
                        <div class="insight-box-title">Catalog Inventory Takeaway</div>
                        Skincare and Makeup make up the vast majority of products in Sephora's inventory (56.4% combined). Fragrance commands the highest premium pricing (Average: $87.26, Median: $80.00) but represents a smaller share of overall listings, indicating a high-margin opportunity. SEPHORA COLLECTION is the volume leader (352 products) with a budget-friendly entry price ($16.38).
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Top 15 Catalog Brands</div>
                    <div class="card-description">Volume leaders in Sephora's inventory. Sephora Collection leads catalog share.</div>
                    <div class="plot-container">
                        <img src="figures/brand_product_counts.png" alt="Top Brands by Product Count">
                    </div>
                </div>
            </div>
            <div class="plot-row-grid">
                <div class="card">
                    <div class="card-title">Category Distribution</div>
                    <div class="plot-container">
                        <img src="figures/category_distribution.png" alt="Category Distribution">
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Price Distribution by Category</div>
                    <div class="plot-container">
                        <img src="figures/price_by_category.png" alt="Price distribution by category">
                    </div>
                </div>
            </div>
        </div>

        <!-- 2. Demographics & Trends Panel -->
        <div id="tab-demographics" class="tab-panel">
            <div class="section-grid">
                <div class="card">
                    <div class="card-title">Reviewer Demographic Profile</div>
                    <div class="card-description">Understanding buyer profiles is key for targeting. Sephora reviewers skew heavily towards Combination skin.</div>
                    <div class="plot-row-grid" style="margin-bottom: 20px;">
                        <div>
                            <h4 style="margin-bottom: 12px; font-family: var(--font-display);">Skin Type Share</h4>
                            <div class="demographics-container">
                                {skin_type_html}
                            </div>
                        </div>
                        <div>
                            <h4 style="margin-bottom: 12px; font-family: var(--font-display);">Top 10 Skin Tones</h4>
                            <div class="demographics-container">
                                {skin_tone_html}
                            </div>
                        </div>
                    </div>
                    <div class="insight-box">
                        <div class="insight-box-title">Demographics Takeaway</div>
                        Combination skin represents nearly half of all customer reviews (49.8%), meaning e-commerce personalization and inventory tagging should heavily prioritize combination-friendly formulations. Review volume peaked in 2020-2021 during lockdowns and exhibits a recurring annual seasonal surge in Nov-Dec.
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Historical Trends</div>
                    <div class="card-description">Review counts peaked during 2020-2021 pandemic lockdowns and show recurrent seasonal shopping spikes.</div>
                    <div class="plot-container">
                        <img src="figures/reviews_over_time.png" alt="Review Volume Over Time">
                    </div>
                </div>
            </div>
            <div class="plot-row-grid">
                <div class="card">
                    <div class="card-title">Demographics Summary Profile</div>
                    <div class="plot-container">
                        <img src="figures/reviewer_profiles.png" alt="Reviewer profiles pie and bar chart">
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Helpfulness Scores by Star Rating</div>
                    <div class="card-description">Reviews with higher ratings are consistently voted as more helpful by the community.</div>
                    <div class="plot-container">
                        <img src="figures/helpfulness_distribution.png" alt="Helpfulness Score Distribution">
                    </div>
                </div>
            </div>
        </div>

        <!-- 3. NLP & Text Mining Panel -->
        <div id="tab-nlp" class="tab-panel">
            <div class="card">
                <div class="card-title">Word Clouds: 5-Star vs 1-Star Reviews</div>
                <div class="card-description">Text analysis shows that satisfied customers emphasize sensory benefits ("love", "feel", "great") while dissatisfied reviews center on product side effects ("dry", "like", "skin").</div>
                <div class="plot-row-grid" style="margin-top: 20px;">
                    <div class="plot-container" style="background-color: white;">
                        <img src="figures/wordcloud_positive.png" alt="Positive Review Wordcloud">
                    </div>
                    <div class="plot-container" style="background-color: white;">
                        <img src="figures/wordcloud_negative.png" alt="Negative Review Wordcloud">
                    </div>
                </div>
            </div>
            <div class="section-grid">
                <div class="card">
                    <div class="card-title">VADER Sentiment Analysis Efficacy</div>
                    <div class="card-description">VADER Compound Sentiment Scores demonstrate a direct monotonic mapping to the Star Ratings. This verifies the validity of the star rating data.</div>
                    <div class="plot-container">
                        <img src="figures/sentiment_vs_rating.png" alt="Sentiment Score vs Rating">
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">VADER Sentiment Metrics</div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>Rating Star</th>
                                    <th>VADER Compound Sentiment</th>
                                    <th>Efficacy Level</th>
                                </tr>
                            </thead>
                            <tbody>
                                <tr>
                                    <td><strong>5 ★</strong></td>
                                    <td><span class="index-badge">{vader["5"]:.3f}</span></td>
                                    <td>Extremely Positive Text</td>
                                </tr>
                                <tr>
                                    <td><strong>4 ★</strong></td>
                                    <td><span class="index-badge">{vader["4"]:.3f}</span></td>
                                    <td>Strong Positive Text</td>
                                </tr>
                                <tr>
                                    <td><strong>3 ★</strong></td>
                                    <td><span class="rating-badge" style="background-color: rgba(241, 196, 15, 0.1); color: var(--warning-color); border-color: rgba(241, 196, 15, 0.3);">{vader["3"]:.3f}</span></td>
                                    <td>Mild Positive / Neutral</td>
                                </tr>
                                <tr>
                                    <td><strong>2 ★</strong></td>
                                    <td><span class="rating-badge bad">{vader["2"]:.3f}</span></td>
                                    <td>Mixed / Conflict Text</td>
                                </tr>
                                <tr>
                                    <td><strong>1 ★</strong></td>
                                    <td><span class="rating-badge bad" style="background-color: rgba(231, 76, 60, 0.2);">{vader["1"]:.3f}</span></td>
                                    <td>Extremely Dissatisfied Text</td>
                                </tr>
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>

        <!-- 4. Strategic Insights Panel -->
        <div id="tab-business" class="tab-panel">
            <div class="insight-highlight-grid">
                <div class="insight-summary-card green">
                    <div class="insight-summary-title">Value Optimization</div>
                    <div class="insight-summary-desc">Sephora Collection and The Ordinary represent maximum customer loyalty relative to prices. Highlight in marketing.</div>
                </div>
                <div class="insight-summary-card yellow">
                    <div class="insight-summary-title">Hidden Gems Campaign</div>
                    <div class="insight-summary-desc">Rare Beauty brush and Fenty gloss trios have extremely high satisfaction but low review volume. Push via email campaigns.</div>
                </div>
                <div class="insight-summary-card red">
                    <div class="insight-summary-title">Luxury Product Audits</div>
                    <div class="insight-summary-desc">Premium luxury items priced over $80 like Dr. Barbara Sturm are generating sub-3-star reviews. R&D reformulation is urgent.</div>
                </div>
            </div>

            <div class="card">
                <div class="card-title">Top 10 Value-for-Money Products</div>
                <div class="card-description">Products maximizing Rating & Loves count relative to retail pricing. Formula: <code>(Rating &times; ln(Loves + 1)) / Price</code></div>
                <div class="table-responsive">
                    <table>
                        <thead>
                            <tr>
                                <th>Product Name</th>
                                <th>Brand</th>
                                <th>Price</th>
                                <th>Rating</th>
                                <th>Loves Count</th>
                                <th>Value Index</th>
                            </tr>
                        </thead>
                        <tbody>
                            {vfm_rows_html}
                        </tbody>
                    </table>
                </div>
                <div class="insight-box success">
                    <div class="insight-box-title">Value Optimization Takeaway</div>
                    SEPHORA COLLECTION (swipes, cotton pads) and The Ordinary (Niacinamide serum) dominate this index, representing exceptional customer value. These products generate massive customer engagement and positive ratings relative to their extremely low unit prices.
                </div>
            </div>

            <div class="section-grid">
                <div class="card">
                    <div class="card-title">Top 10 Hidden Gems</div>
                    <div class="card-description">High rating (&ge; 4.5) with low reviews count (10-50). Candidates for mainstream push.</div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>Product Name</th>
                                    <th>Brand</th>
                                    <th>Price</th>
                                    <th>Rating</th>
                                    <th>Loves Count</th>
                                    <th>Reviews</th>
                                </tr>
                            </thead>
                            <tbody>
                                {gems_rows_html}
                            </tbody>
                        </table>
                    </div>
                    <div class="insight-box warning">
                        <div class="insight-box-title">Hidden Gems Campaign Takeaway</div>
                        Rare Beauty (Blush Brush) and Fenty Beauty (Lip Gloss Trio) produce highly-rated items that have not yet reached high review counts. Spotlighting these products in homepage features or email campaigns offers a high-ROI opportunity to convert highly loyal user groups into mainstream sales.
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Top 10 Overrated Luxury Products</div>
                    <div class="card-description">Price &ge; $80 with ratings &le; 3.5. Brand liability hazards.</div>
                    <div class="table-responsive">
                        <table>
                            <thead>
                                <tr>
                                    <th>Product Name</th>
                                    <th>Brand</th>
                                    <th>Price</th>
                                    <th>Rating</th>
                                    <th>Loves Count</th>
                                    <th>Reviews</th>
                                </tr>
                            </thead>
                            <tbody>
                                {overrated_rows_html}
                            </tbody>
                        </table>
                    </div>
                    <div class="insight-box danger">
                        <div class="insight-box-title">Luxury Product Audit Takeaway</div>
                        Ultra-premium items like Dr. Barbara Sturm Sun Drops ($150, 2.72★) and FOREO LUNA fofo ($89, 2.89★) are major customer friction points. These high-ticket, low-rating products present significant brand liability and should undergo R&D formulation auditing or retail shelf-space reassignment.
                    </div>
                </div>
            </div>
            <div class="card" style="margin-top: 30px;">
                <div class="insight-box">
                    <div class="insight-box-title">Sentiment & Review Efficacy Takeaway</div>
                    Textual sentiment scores align monotonically with star ratings (average sentiment ranges from 0.010 for 1-star to 0.757 for 5-star), confirming rating integrity. Satisfied customers focus on positive sensory elements ("love", "cream", "great"), while dissatisfied reviews center on skin irritation and formulation failures ("dry", "face", "acne").
                </div>
            </div>
            
            <div class="plot-row-grid">
                <div class="card">
                    <div class="card-title">Value-for-Money Ranking</div>
                    <div class="plot-container">
                        <img src="figures/value_for_money.png" alt="Value for Money Plot">
                    </div>
                </div>
                <div class="card">
                    <div class="card-title">Hidden Gems Ranking</div>
                    <div class="plot-container">
                        <img src="figures/hidden_gems.png" alt="Hidden Gems Plot">
                    </div>
                </div>
            </div>
            <div class="card">
                <div class="card-title">Overrated Luxury Products Pricing</div>
                <div class="plot-container">
                    <img src="figures/overrated_products.png" alt="Overrated Products Plot">
                </div>
            </div>
        </div>

    </main>

    <script>
        function switchTab(tabId) {{
            // Deactivate all tabs and panels
            document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
            document.querySelectorAll('.tab-panel').forEach(panel => panel.classList.remove('active'));
            
            // Activate selected tab and panel
            const activeBtn = Array.from(document.querySelectorAll('.tab-btn')).find(btn => btn.innerText.toLowerCase().includes(tabId));
            if (activeBtn) activeBtn.classList.add('active');
            
            const activePanel = document.getElementById('tab-' + tabId);
            if (activePanel) activePanel.classList.add('active');
        }}
    </script>
</body>
</html>
"""
    
    with open("reports/beauty_product_analytics_report.html", "w", encoding="utf-8") as f:
        f.write(html_content)
    print("Saved HTML report dashboard: reports/beauty_product_analytics_report.html")

if __name__ == "__main__":
    generate_reports()
