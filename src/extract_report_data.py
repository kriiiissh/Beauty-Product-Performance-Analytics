import os
import sys
import json
import pandas as pd
import numpy as np
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import re

# Add src to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from src.data_loader import load_products, load_reviews, get_merged_data

def extract_and_save_data():
    print("Loading data...")
    products_df = load_products("data/product_info.csv", verbose=False)
    reviews_no_text = load_reviews("data", include_text=False, verbose=False)
    
    # 1. Catalog Summary Stats
    total_products = len(products_df)
    total_reviews_in_catalog = int(products_df["reviews"].sum())
    total_loves_in_catalog = int(products_df["loves_count"].sum())
    avg_price = float(products_df["price_usd"].mean())
    median_price = float(products_df["price_usd"].median())
    max_price = float(products_df["price_usd"].max())
    min_price = float(products_df["price_usd"].min())
    
    # 2. Missing Values Heatmap data
    missing_counts = products_df.isnull().sum().to_dict()
    
    # 3. Category Distribution
    cat_stats = []
    for cat, group in products_df.groupby("primary_category", observed=True):
        cat_stats.append({
            "category": str(cat),
            "count": int(len(group)),
            "pct": float(len(group) / len(products_df) * 100),
            "avg_price": float(group["price_usd"].mean()),
            "median_price": float(group["price_usd"].median()),
            "avg_rating": float(group["rating"].dropna().mean())
        })
    cat_stats = sorted(cat_stats, key=lambda x: x["count"], reverse=True)
    
    # 4. Top 15 Brands
    brand_counts = products_df["brand_name"].value_counts().head(15)
    brand_stats = []
    for brand in brand_counts.index:
        group = products_df[products_df["brand_name"] == brand]
        brand_stats.append({
            "brand_name": str(brand),
            "count": int(len(group)),
            "avg_price": float(group["price_usd"].mean()),
            "avg_rating": float(group["rating"].dropna().mean()),
            "total_loves": int(group["loves_count"].sum())
        })
        
    # 5. Correlation
    numeric_cols = ["loves_count", "rating", "reviews", "price_usd"]
    corr_matrix = products_df[numeric_cols].corr().to_dict()
    
    # 6. Demographics
    skin_types = reviews_no_text["skin_type"].value_counts(normalize=True).to_dict()
    skin_types_pct = {str(k): float(v * 100) for k, v in skin_types.items()}
    
    skin_tones = reviews_no_text["skin_tone"].value_counts(normalize=True).head(10).to_dict()
    skin_tones_pct = {str(k): float(v * 100) for k, v in skin_tones.items()}
    
    # 7. Review trends over years
    reviews_no_text["year"] = reviews_no_text["submission_time"].dt.year
    yearly_reviews = reviews_no_text["year"].value_counts().sort_index().to_dict()
    yearly_reviews = {str(k): int(v) for k, v in yearly_reviews.items() if pd.notnull(k)}
    
    # 8. Helpfulness Distribution by Rating
    helpfulness_by_rating = {}
    valid_feedback = reviews_no_text[reviews_no_text["total_feedback_count"] >= 5]
    for r, group in valid_feedback.groupby("rating"):
        helpfulness_by_rating[str(r)] = float(group["helpfulness"].mean())
        
    # 9. NLP Review Text Sample stats
    print("Loading review text sample for text-mining stats...")
    reviews_sample = load_reviews("data", include_text=True, verbose=False).sample(20000, random_state=42)
    reviews_sample["char_length"] = reviews_sample["review_text"].str.len()
    reviews_sample["word_count"] = reviews_sample["review_text"].apply(lambda x: len(str(x).split()))
    
    avg_word_count = float(reviews_sample["word_count"].mean())
    median_word_count = float(reviews_sample["word_count"].median())
    
    # Calculate word frequencies for positive (5-star) and negative (1-star) reviews
    print("Analyzing word frequencies...")
    pos_reviews = reviews_sample[reviews_sample["rating"] == 5]["review_text"].astype(str).tolist()[:3000]
    neg_reviews = reviews_sample[reviews_sample["rating"] == 1]["review_text"].astype(str).tolist()[:3000]
    
    stop_words = {"the", "and", "a", "of", "to", "is", "in", "it", "i", "this", "my", "for", "with", "but", "on", "was", "that", "so", "have", "with", "product", "this", "be", "not", "me", "you", "had", "at", "as"}
    
    def get_top_words(texts, top_n=20):
        words = []
        for text in texts:
            text = text.lower()
            text = re.sub(r'[^a-zA-Z\s]', '', text)
            words.extend([w for w in text.split() if w not in stop_words and len(w) > 2])
        return pd.Series(words).value_counts().head(top_n).to_dict()
        
    top_pos_words = get_top_words(pos_reviews)
    top_neg_words = get_top_words(neg_reviews)
    
    # 10. VADER sentiment by rating
    print("Calculating VADER Sentiment scores for sample...")
    analyzer = SentimentIntensityAnalyzer()
    sentiment_df = reviews_sample.sample(5000, random_state=42).copy()
    sentiment_df["vader_compound"] = sentiment_df["review_text"].apply(lambda x: analyzer.polarity_scores(str(x))["compound"])
    
    vader_by_rating = {}
    for r, group in sentiment_df.groupby("rating"):
        vader_by_rating[str(r)] = float(group["vader_compound"].mean())
        
    # 11. Custom Strategic Metrics
    print("Calculating strategic business metrics...")
    
    # Value for Money
    valid_products = products_df[(products_df["price_usd"] > 0) & (products_df["reviews"] > 10)].copy()
    valid_products["value_index"] = (valid_products["rating"] * np.log1p(valid_products["loves_count"])) / valid_products["price_usd"]
    
    top_value = valid_products.sort_values(by="value_index", ascending=False).head(10)
    top_value_list = []
    for idx, row in top_value.iterrows():
        top_value_list.append({
            "product_name": str(row["product_name"]),
            "brand_name": str(row["brand_name"]),
            "price_usd": float(row["price_usd"]),
            "rating": float(row["rating"]),
            "loves_count": int(row["loves_count"]),
            "reviews": int(row["reviews"]),
            "value_index": float(row["value_index"])
        })
        
    # Hidden Gems
    hidden_gems = products_df[
        (products_df["rating"] >= 4.5) & 
        (products_df["reviews"] >= 10) & 
        (products_df["reviews"] <= 50)
    ].sort_values(by="loves_count", ascending=False).head(10)
    
    hidden_gems_list = []
    for idx, row in hidden_gems.iterrows():
        hidden_gems_list.append({
            "product_name": str(row["product_name"]),
            "brand_name": str(row["brand_name"]),
            "price_usd": float(row["price_usd"]),
            "rating": float(row["rating"]),
            "loves_count": int(row["loves_count"]),
            "reviews": int(row["reviews"])
        })
        
    # Overrated Products
    overrated = products_df[
        (products_df["price_usd"] >= 80) & 
        (products_df["rating"] <= 3.5) & 
        (products_df["reviews"] >= 30)
    ].sort_values(by="rating", ascending=True).head(10)
    
    overrated_list = []
    for idx, row in overrated.iterrows():
        overrated_list.append({
            "product_name": str(row["product_name"]),
            "brand_name": str(row["brand_name"]),
            "price_usd": float(row["price_usd"]),
            "rating": float(row["rating"]),
            "loves_count": int(row["loves_count"]),
            "reviews": int(row["reviews"])
        })
        
    # Combine everything
    report_data = {
        "catalog_summary": {
            "total_products": total_products,
            "total_reviews": total_reviews_in_catalog,
            "total_loves": total_loves_in_catalog,
            "avg_price": avg_price,
            "median_price": median_price,
            "max_price": max_price,
            "min_price": min_price
        },
        "missing_values": missing_counts,
        "category_stats": cat_stats,
        "brand_stats": brand_stats,
        "correlation": corr_matrix,
        "demographics": {
            "skin_types": skin_types_pct,
            "skin_tones": skin_tones_pct
        },
        "yearly_reviews": yearly_reviews,
        "helpfulness_by_rating": helpfulness_by_rating,
        "nlp_stats": {
            "avg_word_count": avg_word_count,
            "median_word_count": median_word_count,
            "top_positive_words": top_pos_words,
            "top_negative_words": top_neg_words
        },
        "vader_by_rating": vader_by_rating,
        "business_insights": {
            "value_for_money": top_value_list,
            "hidden_gems": hidden_gems_list,
            "overrated": overrated_list
        }
    }
    
    os.makedirs("data", exist_ok=True)
    with open("data/report_data.json", "w", encoding="utf-8") as f:
        json.dump(report_data, f, indent=4)
        
    print("Report data successfully saved to data/report_data.json")

if __name__ == "__main__":
    extract_and_save_data()
