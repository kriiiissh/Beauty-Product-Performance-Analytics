import os
import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from wordcloud import WordCloud
import glob
from collections import Counter
import re

# Add src to system path to import local modules
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data_loader import load_products, load_reviews, get_merged_data
from src.viz_utils import set_custom_style, save_figure, get_sephora_colors

def run_analysis_pipeline():
    print("="*60)
    print("STARTING SEPHORA EDA ANALYSIS PIPELINE")
    print("="*60)
    
    # 0. Set Custom Styling
    set_custom_style()
    colors = get_sephora_colors()
    
    # Create reports/figures directory if not exists
    os.makedirs("reports/figures", exist_ok=True)
    
    # ==========================================
    # MODULE 1: Data Overview & Memory Profiling
    # ==========================================
    print("\n--- Running Module 1: Data Overview ---")
    
    # Load products (with memory profiling output)
    products_df = load_products("data/product_info.csv", verbose=True)
    
    # Load reviews without text first to show memory difference
    reviews_no_text = load_reviews("data", include_text=False, verbose=True)
    
    # Verify missing values
    missing_products = products_df.isnull().sum()
    print("Product columns missing values:\n", missing_products[missing_products > 0])
    
    # missingno missingness matrix equivalent using seaborn
    plt.figure(figsize=(12, 6))
    sns.heatmap(products_df.isnull(), cbar=False, yticklabels=False, cmap="viridis")
    plt.title("Products Missing Values Heatmap")
    plt.tight_layout()
    plt.savefig("reports/figures/missing_values_heatmap.png", dpi=300)
    plt.close()
    print("Saved: missing_values_heatmap.png")
    
    # ==========================================
    # MODULE 2: Product Catalog Analysis
    # ==========================================
    print("\n--- Running Module 2: Product Catalog Analysis ---")
    
    # Category Distribution (Primary Categories)
    plt.figure(figsize=(10, 6))
    cat_counts = products_df["primary_category"].value_counts()
    sns.barplot(x=cat_counts.values, y=cat_counts.index, palette="magma")
    plt.title("Product Distribution by Primary Category", fontsize=14, weight="bold")
    plt.xlabel("Number of Products", fontsize=12)
    plt.ylabel("Category", fontsize=12)
    plt.tight_layout()
    plt.savefig("reports/figures/category_distribution.png", dpi=300)
    plt.close()
    print("Saved: category_distribution.png")
    
    # Price Distribution by Primary Category (Violin / Box Plot)
    plt.figure(figsize=(12, 6))
    # Filtering for products under $150 for readability, as outliers stretch the plot
    filtered_price_df = products_df[products_df["price_usd"] <= 150]
    sns.boxplot(
        data=filtered_price_df,
        x="price_usd",
        y="primary_category",
        palette="crest"
    )
    plt.title("Price Distribution by Primary Category (Products <= $150)", fontsize=14, weight="bold")
    plt.xlabel("Price (USD)", fontsize=12)
    plt.ylabel("Category", fontsize=12)
    plt.tight_layout()
    plt.savefig("reports/figures/price_by_category.png", dpi=300)
    plt.close()
    print("Saved: price_by_category.png")
    
    # Brand product counts (Top 15 brands)
    top_brands = products_df["brand_name"].value_counts().head(15).reset_index()
    top_brands.columns = ["brand_name", "product_count"]
    
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=top_brands,
        x="product_count",
        y="brand_name",
        palette="flare"
    )
    plt.title("Top 15 Brands by Product Count", fontsize=14, weight="bold")
    plt.xlabel("Product Count", fontsize=12)
    plt.ylabel("Brand Name", fontsize=12)
    plt.tight_layout()
    plt.savefig("reports/figures/brand_product_counts.png", dpi=300)
    plt.close()
    print("Saved: brand_product_counts.png")
    
    # Correlation Heatmap for Numeric Columns
    plt.figure(figsize=(10, 8))
    numeric_cols = ["loves_count", "rating", "reviews", "price_usd", "child_count"]
    corr = products_df[numeric_cols].corr()
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", square=True, linewidths=0.5)
    plt.title("Correlation Matrix of Product Features", fontsize=14, weight="bold")
    plt.tight_layout()
    plt.savefig("reports/figures/correlation_heatmap.png", dpi=300)
    plt.close()
    print("Saved: correlation_heatmap.png")
    
    # ==========================================
    # MODULE 3: Review Analysis
    # ==========================================
    print("\n--- Running Module 3: Review Analysis ---")
    
    # Monthly Review Volume Trend
    # Downsample reviews to speed up datetime conversion if necessary, but data_loader did it already
    # Let's count reviews by Month
    reviews_no_text["year_month"] = reviews_no_text["submission_time"].dt.to_period("M")
    monthly_reviews = reviews_no_text.groupby("year_month").size().reset_index(name="review_count")
    # Convert period back to string/datetime for plotting
    monthly_reviews["year_month"] = monthly_reviews["year_month"].astype(str)
    
    plt.figure(figsize=(14, 6))
    # Filter to last 5 years of reviews to avoid sparse old data
    recent_monthly = monthly_reviews.tail(60)
    sns.lineplot(
        data=recent_monthly,
        x="year_month",
        y="review_count",
        marker="o",
        color=colors["primary"],
        linewidth=2
    )
    plt.title("Monthly Review Volume Trend (Last 5 Years)", fontsize=14, weight="bold")
    plt.xticks(rotation=45, ha="right")
    plt.xlabel("Year-Month", fontsize=12)
    plt.ylabel("Review Count", fontsize=12)
    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()
    plt.savefig("reports/figures/reviews_over_time.png", dpi=300)
    plt.close()
    print("Saved: reviews_over_time.png")
    
    # Reviewer Demographics Profile (Skin Type & Tone)
    fig, axes = plt.subplots(1, 2, figsize=(16, 6))
    
    skin_type_counts = reviews_no_text[reviews_no_text["skin_type"] != "Unknown"]["skin_type"].value_counts()
    axes[0].pie(skin_type_counts, labels=skin_type_counts.index, autopct="%1.1f%%", colors=sns.color_palette("pastel"), startangle=140)
    axes[0].set_title("Reviewer Distribution by Skin Type", fontsize=12, weight="bold")
    
    skin_tone_counts = reviews_no_text[reviews_no_text["skin_tone"] != "Unknown"]["skin_tone"].value_counts().head(10)
    sns.barplot(x=skin_tone_counts.values, y=skin_tone_counts.index, ax=axes[1], palette="copper")
    axes[1].set_title("Top Reviewer Skin Tones", fontsize=12, weight="bold")
    axes[1].set_xlabel("Review Count")
    
    plt.tight_layout()
    plt.savefig("reports/figures/reviewer_profiles.png", dpi=300)
    plt.close()
    print("Saved: reviewer_profiles.png")
    
    # Helpfulness Distribution & Drivers
    # Helpfulness ratio vs rating
    plt.figure(figsize=(10, 6))
    sns.boxplot(
        data=reviews_no_text[reviews_no_text["total_feedback_count"] > 5],
        x="rating",
        y="helpfulness",
        palette="viridis"
    )
    plt.title("Review Helpfulness Score by Star Rating (Minimum 5 Feedback Votes)", fontsize=14, weight="bold")
    plt.xlabel("Review Rating (Stars)", fontsize=12)
    plt.ylabel("Helpfulness Score", fontsize=12)
    plt.tight_layout()
    plt.savefig("reports/figures/helpfulness_distribution.png", dpi=300)
    plt.close()
    print("Saved: helpfulness_distribution.png")
    
    # ==========================================
    # MODULE 4: NLP & Sentiment Analysis
    # ==========================================
    print("\n--- Running Module 4: NLP & Sentiment Analysis ---")
    
    # Load review dataset WITH text, sampling 50,000 rows for speed and efficiency
    print("Loading review text sample for NLP...")
    reviews_sample = load_reviews("data", include_text=True, verbose=False).sample(50000, random_state=42)
    
    # Review length distribution
    reviews_sample["char_length"] = reviews_sample["review_text"].str.len()
    reviews_sample["word_length"] = reviews_sample["review_text"].apply(lambda x: len(str(x).split()))
    
    # Wordcloud for 5-star vs 1-star reviews
    pos_text = " ".join(reviews_sample[reviews_sample["rating"] == 5]["review_text"].astype(str).tolist()[:5000])
    neg_text = " ".join(reviews_sample[reviews_sample["rating"] == 1]["review_text"].astype(str).tolist()[:5000])
    
    # Clean text helper
    def clean_text(text):
        text = text.lower()
        text = re.sub(r'[^a-zA-Z\s]', '', text)
        stop_words = {"the", "and", "a", "of", "to", "is", "in", "it", "i", "this", "my", "for", "with", "but", "on", "was", "this", "that", "so", "have", "with"}
        words = [w for w in text.split() if w not in stop_words and len(w) > 2]
        return " ".join(words)
        
    cleaned_pos = clean_text(pos_text)
    cleaned_neg = clean_text(neg_text)
    
    # Positive wordcloud
    plt.figure(figsize=(10, 5))
    wc_pos = WordCloud(width=800, height=400, background_color="white", colormap="summer", max_words=100).generate(cleaned_pos)
    plt.imshow(wc_pos, interpolation="bilinear")
    plt.axis("off")
    plt.title("Top Words in 5-Star Reviews", fontsize=16, weight="bold", pad=15)
    plt.tight_layout()
    plt.savefig("reports/figures/wordcloud_positive.png", dpi=300)
    plt.close()
    print("Saved: wordcloud_positive.png")
    
    # Negative wordcloud
    plt.figure(figsize=(10, 5))
    wc_neg = WordCloud(width=800, height=400, background_color="white", colormap="autumn", max_words=100).generate(cleaned_neg)
    plt.imshow(wc_neg, interpolation="bilinear")
    plt.axis("off")
    plt.title("Top Words in 1-Star Reviews", fontsize=16, weight="bold", pad=15)
    plt.tight_layout()
    plt.savefig("reports/figures/wordcloud_negative.png", dpi=300)
    plt.close()
    print("Saved: wordcloud_negative.png")
    
    # VADER Sentiment Scoring
    print("Calculating VADER Sentiment scores...")
    analyzer = SentimentIntensityAnalyzer()
    
    # VADER is fast enough on 10,000 rows
    sentiment_df = reviews_sample.sample(10000, random_state=42).copy()
    sentiment_df["vader_compound"] = sentiment_df["review_text"].apply(lambda x: analyzer.polarity_scores(str(x))["compound"])
    
    # Plot Sentiment vs Star Rating
    plt.figure(figsize=(10, 6))
    sns.boxplot(
        data=sentiment_df,
        x="rating",
        y="vader_compound",
        palette="coolwarm"
    )
    plt.title("VADER Sentiment Score by Review Rating", fontsize=14, weight="bold")
    plt.xlabel("Review Rating (Stars)", fontsize=12)
    plt.ylabel("VADER Compound Sentiment Score", fontsize=12)
    plt.tight_layout()
    plt.savefig("reports/figures/sentiment_vs_rating.png", dpi=300)
    plt.close()
    print("Saved: sentiment_vs_rating.png")
    
    # ==========================================
    # MODULE 5: Business Insights
    # ==========================================
    print("\n--- Running Module 5: Business Insights ---")
    
    # Joint analysis
    merged_df = get_merged_data(products_df, reviews_no_text)
    
    # Value for Money Index
    # We can create a metric: value_index = rating * log(loves_count + 1) / price_usd
    # Let's filter products with positive price and some minimum level of ratings
    valid_products = products_df[(products_df["price_usd"] > 0) & (products_df["reviews"] > 10)].copy()
    valid_products["value_index"] = (valid_products["rating"] * np.log1p(valid_products["loves_count"])) / valid_products["price_usd"]
    
    # Top 10 Value for Money products
    top_value = valid_products.sort_values(by="value_index", ascending=False).head(10)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=top_value,
        x="value_index",
        y="product_name",
        palette="summer"
    )
    plt.title("Top 10 Value for Money Products (High Rating + Engagement / Price)", fontsize=14, weight="bold")
    plt.xlabel("Value for Money Index", fontsize=12)
    plt.ylabel("Product Name", fontsize=12)
    plt.tight_layout()
    plt.savefig("reports/figures/value_for_money.png", dpi=300)
    plt.close()
    print("Saved: value_for_money.png")
    
    # Hidden Gems
    # High rating (>= 4.5), low but sufficient review count (10 to 50 reviews)
    hidden_gems = products_df[
        (products_df["rating"] >= 4.5) & 
        (products_df["reviews"] >= 10) & 
        (products_df["reviews"] <= 50)
    ].sort_values(by="loves_count", ascending=False).head(10)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(
        data=hidden_gems,
        x="loves_count",
        y="product_name",
        palette="viridis"
    )
    plt.title("Top 10 'Hidden Gems' (Highly Rated, 10-50 Reviews, Sorted by Loves)", fontsize=14, weight="bold")
    plt.xlabel("Loves Count (User Engagement)", fontsize=12)
    plt.ylabel("Product Name", fontsize=12)
    plt.tight_layout()
    plt.savefig("reports/figures/hidden_gems.png", dpi=300)
    plt.close()
    print("Saved: hidden_gems.png")
    
    # Overrated Products
    # High price (>= $80), low rating (<= 3.5), high number of reviews (>= 30 reviews)
    overrated = products_df[
        (products_df["price_usd"] >= 80) & 
        (products_df["rating"] <= 3.5) & 
        (products_df["reviews"] >= 30)
    ].sort_values(by="rating", ascending=True).head(10)
    
    if len(overrated) > 0:
        plt.figure(figsize=(12, 6))
        sns.barplot(
            data=overrated,
            x="price_usd",
            y="product_name",
            palette="autumn"
        )
        plt.title("Top Overrated Luxury Products (Price >= $80, Rating <= 3.5)", fontsize=14, weight="bold")
        plt.xlabel("Price (USD)", fontsize=12)
        plt.ylabel("Product Name", fontsize=12)
        plt.tight_layout()
        plt.savefig("reports/figures/overrated_products.png", dpi=300)
        plt.close()
        print("Saved: overrated_products.png")
    else:
        print("No overrated products found matching threshold. Creating default blank plot.")
        plt.figure(figsize=(10, 6))
        plt.text(0.5, 0.5, "No Luxury Products Match Overrated Criteria (Price >= $80, Rating <= 3.5)", 
                 ha="center", va="center", fontsize=12, style="italic")
        plt.savefig("reports/figures/overrated_products.png", dpi=300)
        plt.close()
        
    print("="*60)
    print("ALL MODULES SUCCESSFULLY PROCESSED AND VISUALIZATIONS GENERATED!")
    print("="*60)

if __name__ == "__main__":
    run_analysis_pipeline()
