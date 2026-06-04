import os
import glob
import pandas as pd
import numpy as np
from tqdm import tqdm

def load_products(filepath="data/product_info.csv", verbose=True):
    """
    Loads and optimizes product_info.csv dataset.
    
    Parameters:
    -----------
    filepath : str
        Path to the product_info.csv file.
    verbose : bool
        Whether to print memory optimization reports.
        
    Returns:
    --------
    pd.DataFrame
        Clean and memory-optimized products DataFrame.
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"Product info file not found at {filepath}")
        
    if verbose:
        print(f"Loading products from {filepath}...")
        
    # Read CSV
    df = pd.read_csv(filepath)
    orig_memory = df.memory_usage(deep=True).sum() / (1024 ** 2)
    
    # 1. Clean binary/boolean flags
    bool_cols = ["limited_edition", "new", "online_only", "out_of_stock", "sephora_exclusive"]
    for col in bool_cols:
        if col in df.columns:
            # Fill missing with False, convert to bool
            df[col] = df[col].fillna(0).astype(bool)
            
    # 2. Downcast numeric columns
    numeric_downcasts = {
        "loves_count": "int32",
        "reviews": "int32",
        "rating": "float32",
        "price_usd": "float32",
        "value_price_usd": "float32",
        "sale_price_usd": "float32",
        "child_count": "int16",
        "child_max_price": "float32",
        "child_min_price": "float32"
    }
    
    for col, dtype in numeric_downcasts.items():
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
            if "int" in dtype:
                df[col] = df[col].fillna(0).astype(dtype)
            else:
                df[col] = df[col].astype(dtype)
                
    # 3. Categorical optimization for categories & variations
    cat_cols = ["primary_category", "secondary_category", "tertiary_category", "variation_type"]
    for col in cat_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype("category")
            
    # 4. Handle text columns (strings)
    str_cols = ["product_name", "brand_id", "brand_name", "size", "variation_value", "variation_desc", "ingredients", "highlights"]
    for col in str_cols:
        if col in df.columns:
            df[col] = df[col].fillna("")
            
    opt_memory = df.memory_usage(deep=True).sum() / (1024 ** 2)
    
    if verbose:
        print(f"Products shape: {df.shape}")
        print(f"Memory: {orig_memory:.2f} MB -> {opt_memory:.2f} MB (Saved: {(1 - opt_memory/orig_memory)*100:.1f}%)")
        
    return df

def load_reviews(data_dir="data", include_text=True, verbose=True):
    """
    Finds and loads all reviews_*.csv files, concatenates them,
    and applies heavy memory optimization and type coercion.
    
    Parameters:
    -----------
    data_dir : str
        Directory where reviews CSV files are stored.
    include_text : bool
        If False, drops 'review_text' and 'review_title' to save ~80% RAM.
        Highly recommended for non-NLP notebooks.
    verbose : bool
        Whether to print memory optimization reports.
        
    Returns:
    --------
    pd.DataFrame
        Concatenated and memory-optimized reviews DataFrame.
    """
    search_path = os.path.join(data_dir, "reviews_*.csv")
    csv_files = glob.glob(search_path)
    
    if not csv_files:
        raise FileNotFoundError(f"No reviews_*.csv files found in directory {data_dir}")
        
    if verbose:
        print(f"Found {len(csv_files)} review files. Loading sequentially...")
        
    dfs = []
    
    # Columns we definitely want to drop or downcast
    # We drop product_name, brand_name, price_usd because they are duplicate values from products table
    cols_to_use = [
        "author_id", "rating", "is_recommended", "helpfulness",
        "total_feedback_count", "total_neg_feedback_count",
        "total_pos_feedback_count", "submission_time",
        "skin_tone", "eye_color", "skin_type", "hair_color", "product_id"
    ]
    
    if include_text:
        cols_to_use.extend(["review_text", "review_title"])
        
    for file in tqdm(csv_files, desc="Reading reviews CSVs", disable=not verbose):
        # Read only specific columns to save memory from the start
        df_chunk = pd.read_csv(file, usecols=lambda c: c in cols_to_use, low_memory=False)
        dfs.append(df_chunk)
        
    df = pd.concat(dfs, ignore_index=True)
    orig_memory = df.memory_usage(deep=True).sum() / (1024 ** 2)
    
    # Clean and Downcast Columns
    # 1. rating: ranges from 1 to 5
    df["rating"] = pd.to_numeric(df["rating"], errors="coerce").fillna(0).astype("int8")
    
    # 2. is_recommended: True/False/NaN. Use nullable boolean type
    df["is_recommended"] = df["is_recommended"].astype("boolean")
    
    # 3. feedback counts: int32
    counts_cols = ["total_feedback_count", "total_neg_feedback_count", "total_pos_feedback_count"]
    for col in counts_cols:
        if col in df.columns:
            df[col] = df[col].fillna(0).astype("int32")
            
    # 4. helpfulness: float32
    if "helpfulness" in df.columns:
        df["helpfulness"] = df["helpfulness"].astype("float32")
        
    # 5. submission_time: datetime
    if "submission_time" in df.columns:
        df["submission_time"] = pd.to_datetime(df["submission_time"], errors="coerce")
        
    # 6. Demographics: category dtype saves massive RAM
    demo_cols = ["skin_tone", "eye_color", "skin_type", "hair_color"]
    for col in demo_cols:
        if col in df.columns:
            df[col] = df[col].fillna("Unknown").astype("category")
            
    # 7. product_id: category (as there are only 8494 products, string IDs take a lot of space)
    if "product_id" in df.columns:
        df["product_id"] = df["product_id"].astype("category")
        
    # 8. Text columns
    if include_text:
        for col in ["review_text", "review_title"]:
            if col in df.columns:
                df[col] = df[col].fillna("")
                
    opt_memory = df.memory_usage(deep=True).sum() / (1024 ** 2)
    
    if verbose:
        print(f"Reviews shape: {df.shape}")
        print(f"Memory: {orig_memory:.2f} MB -> {opt_memory:.2f} MB (Saved: {(1 - opt_memory/orig_memory)*100:.1f}%)")
        
    return df

def get_merged_data(products_df, reviews_df):
    """
    Merges products and reviews on product_id.
    
    Parameters:
    -----------
    products_df : pd.DataFrame
    reviews_df : pd.DataFrame
    
    Returns:
    --------
    pd.DataFrame
        Merged DataFrame.
    """
    # product_id is categorical in reviews, make sure it matches product_id type (or convert to category in merge)
    if not isinstance(products_df["product_id"].dtype, pd.CategoricalDtype):
        products_df = products_df.copy()
        products_df["product_id"] = products_df["product_id"].astype("category")
        
    merged = pd.merge(reviews_df, products_df, on="product_id", how="inner", suffixes=("_review", "_product"))
    return merged
