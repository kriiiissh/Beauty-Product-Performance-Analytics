import os
import json

def create_notebook(cells, filepath):
    """
    Writes a list of cell definitions into a Jupyter Notebook JSON file.
    """
    notebook = {
        "cells": cells,
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3 (ipykernel)",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "name": "python"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 2
    }
    
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(notebook, f, indent=1)
    print(f"Created notebook: {filepath}")

def build_notebook_01():
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Sephora E-Commerce EDA: 01 - Data Overview & Quality Audit\n",
                "\n",
                "This notebook provides a detailed inspection of the raw datasets, checking schemas, data dimensions, missingness patterns, and executing a **memory downcasting optimization pipeline** to handle our 1M+ reviews efficiently."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import sys\n",
                "import os\n",
                "# Add project root directory to python path\n",
                "sys.path.append(os.path.abspath(\"..\"))\n",
                "\n",
                "import pandas as pd\n",
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "import missingno as msno\n",
                "\n",
                "from src.data_loader import load_products, load_reviews\n",
                "from src.viz_utils import set_custom_style\n",
                "\n",
                "# Configure default plotting aesthetics\n",
                "set_custom_style()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Load Sephora Products Info"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "products_df = load_products(\"../data/product_info.csv\")\n",
                "products_df.head(5)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Load Reviews Dataset\n",
                "\n",
                "We can selectively include review text. Let's load the reviews dataset without text first to check metadata features. Notice the optimized memory consumption printed by the loader."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "reviews_df = load_reviews(\"../data\", include_text=False)\n",
                "reviews_df.head(5)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Data Schema and Types Audit"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "print(\"=== PRODUCTS DATA SCHEMA ===\")\n",
                "products_df.info()\n",
                "\n",
                "print(\"\\n\" + \"=\"*40 + \"\\n=== REVIEWS DATA SCHEMA ===\")\n",
                "reviews_df.info()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Missing Values Analysis\n",
                "\n",
                "Let's identify missing values across features using `missingno` to map missingness in our product catalog."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "plt.figure(figsize=(10, 6))\n",
                "msno.matrix(products_df, sparkline=False, color=(0.1, 0.1, 0.1))\n",
                "plt.title(\"Products Missing Value Map\", fontsize=16, pad=15)\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 5. Summary Statistics"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "print(\"=== PRODUCTS NUMERIC SUMMARY ===\")\n",
                "products_df.describe().T\n",
                "\n",
                "print(\"\\n=== REVIEWS NUMERIC SUMMARY ===\")\n",
                "reviews_df.describe().T"
            ]
        }
    ]
    create_notebook(cells, "notebooks/01_data_overview.ipynb")

def build_notebook_02():
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Sephora E-Commerce EDA: 02 - Product Catalog Analysis\n",
                "\n",
                "This notebook analyzes Sephora's product catalog. We examine category hierarchy, price distribution (to find luxury pricing tiers), top brands, loves count, and flags like exclusives."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import sys\n",
                "import os\n",
                "sys.path.append(os.path.abspath(\"..\"))\n",
                "\n",
                "import pandas as pd\n",
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "\n",
                "from src.data_loader import load_products\n",
                "from src.viz_utils import set_custom_style, save_figure\n",
                "\n",
                "set_custom_style()\n",
                "products_df = load_products(\"../data/product_info.csv\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Category Breakdown\n",
                "\n",
                "Let's see what primary categories make up Sephora's inventory."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "plt.figure(figsize=(10, 6))\n",
                "cat_counts = products_df[\"primary_category\"].value_counts()\n",
                "sns.barplot(x=cat_counts.values, y=cat_counts.index, palette=\"magma\")\n",
                "plt.title(\"Product Count by Primary Category\", fontsize=14, weight=\"bold\")\n",
                "plt.xlabel(\"Count\")\n",
                "plt.ylabel(\"Primary Category\")\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Price Distribution by Category\n",
                "\n",
                "We look at prices by category. We limit our view to products <= $150 to remove extreme pricing outliers (like large sets) for better visual scale."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "plt.figure(figsize=(12, 6))\n",
                "filtered_price_df = products_df[products_df[\"price_usd\"] <= 150]\n",
                "sns.boxplot(data=filtered_price_df, x=\"price_usd\", y=\"primary_category\", palette=\"crest\")\n",
                "plt.title(\"Price Distribution by Category (Products <= $150)\", fontsize=14, weight=\"bold\")\n",
                "plt.xlabel(\"Price (USD)\")\n",
                "plt.ylabel(\"Category\")\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Brand Representation\n",
                "\n",
                "Let's see who are the top 15 brands by product counts."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "top_brands = products_df[\"brand_name\"].value_counts().head(15).reset_index()\n",
                "top_brands.columns = [\"brand_name\", \"count\"]\n",
                "\n",
                "plt.figure(figsize=(12, 6))\n",
                "sns.barplot(data=top_brands, x=\"count\", y=\"brand_name\", palette=\"flare\")\n",
                "plt.title(\"Top 15 Brands by Product Count in Sephora Catalog\", fontsize=14, weight=\"bold\")\n",
                "plt.xlabel(\"Number of Products\")\n",
                "plt.ylabel(\"Brand Name\")\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 4. Correlation Matrix of Numeric Attributes"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "plt.figure(figsize=(10, 8))\n",
                "numeric_cols = [\"loves_count\", \"rating\", \"reviews\", \"price_usd\", \"child_count\"]\n",
                "sns.heatmap(products_df[numeric_cols].corr(), annot=True, cmap=\"coolwarm\", fmt=\".2f\", square=True)\n",
                "plt.title(\"Correlation Matrix of Product Catalog Attributes\", fontsize=14, weight=\"bold\")\n",
                "plt.show()"
            ]
        }
    ]
    create_notebook(cells, "notebooks/02_product_analysis.ipynb")

def build_notebook_03():
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Sephora E-Commerce EDA: 03 - Review & Reviewer Profile Deep Dive\n",
                "\n",
                "This notebook focuses on the review-level data (~1.1M records). We inspect reviews volume over time (seasonality), reviewer demographics (skin profile, hair color), and factors influencing review helpfulness."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import sys\n",
                "import os\n",
                "sys.path.append(os.path.abspath(\"..\"))\n",
                "\n",
                "import pandas as pd\n",
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "\n",
                "from src.data_loader import load_reviews\n",
                "from src.viz_utils import set_custom_style\n",
                "\n",
                "set_custom_style()\n",
                "reviews_df = load_reviews(\"../data\", include_text=False)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Reviews Volume Over Time\n",
                "\n",
                "Let's see if there is any holiday season spikes (e.g. November/December) in Sephora's reviews volume."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "reviews_df[\"year_month\"] = reviews_df[\"submission_time\"].dt.to_period(\"M\")\n",
                "monthly_reviews = reviews_df.groupby(\"year_month\").size().reset_index(name=\"count\")\n",
                "monthly_reviews[\"year_month\"] = monthly_reviews[\"year_month\"].astype(str)\n",
                "\n",
                "# Line plot showing review count trends over the last 5 years\n",
                "plt.figure(figsize=(14, 6))\n",
                "sns.lineplot(data=monthly_reviews.tail(60), x=\"year_month\", y=\"count\", marker=\"o\", color=\"#FF3366\", linewidth=2)\n",
                "plt.title(\"Monthly Reviews Volume Trend (Last 5 Years)\", fontsize=14, weight=\"bold\")\n",
                "plt.xticks(rotation=45, ha=\"right\")\n",
                "plt.xlabel(\"Year-Month\")\n",
                "plt.ylabel(\"Number of Reviews\")\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Reviewer Demographic Profiles\n",
                "\n",
                "Sephora reviews contain customer profiles like skin type, skin tone, hair color, and eye color. Let's analyze who is buying and reviewing these cosmetics."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "fig, axes = plt.subplots(1, 2, figsize=(16, 6))\n",
                "\n",
                "skin_type_counts = reviews_df[reviews_df[\"skin_type\"] != \"Unknown\"][\"skin_type\"].value_counts()\n",
                "axes[0].pie(skin_type_counts, labels=skin_type_counts.index, autopct=\"%1.1f%%\", colors=sns.color_palette(\"pastel\"), startangle=140)\n",
                "axes[0].set_title(\"Reviewers by Skin Type\", fontsize=12, weight=\"bold\")\n",
                "\n",
                "skin_tone_counts = reviews_df[reviews_df[\"skin_tone\"] != \"Unknown\"][\"skin_tone\"].value_counts().head(10)\n",
                "sns.barplot(x=skin_tone_counts.values, y=skin_tone_counts.index, ax=axes[1], palette=\"copper\")\n",
                "axes[1].set_title(\"Top Reviewer Skin Tones\", fontsize=12, weight=\"bold\")\n",
                "axes[1].set_xlabel(\"Review Counts\")\n",
                "plt.tight_layout()\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Review Helpfulness Analysis\n",
                "\n",
                "What makes a review helpful? Let's check the helpfulness score (which is a ratio of positive feedback to total feedback) across ratings."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "plt.figure(figsize=(10, 6))\n",
                "# Minimum 5 feedback votes to avoid ratio skewness (like 1/1 being 100% helpful)\n",
                "sns.boxplot(data=reviews_df[reviews_df[\"total_feedback_count\"] >= 5], x=\"rating\", y=\"helpfulness\", palette=\"viridis\")\n",
                "plt.title(\"Helpfulness Score Distribution by Review Rating (Stars)\", fontsize=14, weight=\"bold\")\n",
                "plt.xlabel(\"Review Rating (Stars)\")\n",
                "plt.ylabel(\"Helpfulness Score (Ratio)\")\n",
                "plt.show()"
            ]
        }
    ]
    create_notebook(cells, "notebooks/03_review_analysis.ipynb")

def build_notebook_04():
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Sephora E-Commerce EDA: 04 - NLP & Sentiment analysis\n",
                "\n",
                "This notebook analyzes the review text itself. We downsample the dataset to 50k rows for faster tokenization, clean strings, build Word Clouds of positive/negative reviews, and calculate sentiment scores using VADER."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import sys\n",
                "import os\n",
                "sys.path.append(os.path.abspath(\"..\"))\n",
                "\n",
                "import pandas as pd\n",
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "from wordcloud import WordCloud\n",
                "from nltk.sentiment.vader import SentimentIntensityAnalyzer\n",
                "import re\n",
                "\n",
                "from src.data_loader import load_reviews\n",
                "from src.viz_utils import set_custom_style\n",
                "\n",
                "set_custom_style()\n",
                "\n",
                "# Load reviews with text, sample 50,000 for speed\n",
                "reviews_sample = load_reviews(\"../data\", include_text=True, verbose=False).sample(50000, random_state=42)"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Review Word Length Distribution"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "reviews_sample[\"word_count\"] = reviews_sample[\"review_text\"].apply(lambda x: len(str(x).split()))\n",
                "\n",
                "plt.figure(figsize=(10, 6))\n",
                "sns.histplot(data=reviews_sample[reviews_sample[\"word_count\"] <= 150], x=\"word_count\", kde=True, color=\"#FF3366\", bins=50)\n",
                "plt.title(\"Distribution of Review Word Counts (Reviews <= 150 Words)\", fontsize=14, weight=\"bold\")\n",
                "plt.xlabel(\"Word Count\")\n",
                "plt.ylabel(\"Count\")\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Text Mining: Top Words in 5-Star vs 1-Star Reviews"
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "pos_reviews = \" \".join(reviews_sample[reviews_sample[\"rating\"] == 5][\"review_text\"].astype(str).tolist()[:5000])\n",
                "neg_reviews = \" \".join(reviews_sample[reviews_sample[\"rating\"] == 1][\"review_text\"].astype(str).tolist()[:5000])\n",
                "\n",
                "def clean_text(text):\n",
                "    text = text.lower()\n",
                "    text = re.sub(r'[^a-zA-Z\\s]', '', text)\n",
                "    stop_words = {\"the\", \"and\", \"a\", \"of\", \"to\", \"is\", \"in\", \"it\", \"i\", \"this\", \"my\", \"for\", \"with\", \"but\", \"on\", \"was\", \"that\", \"so\", \"have\", \"with\", \"product\"}\n",
                "    return \" \".join([w for w in text.split() if w not in stop_words and len(w) > 2])\n",
                "\n",
                "cleaned_pos = clean_text(pos_reviews)\n",
                "cleaned_neg = clean_text(neg_reviews)\n",
                "\n",
                "# Generate Word Clouds\n",
                "wc_pos = WordCloud(width=800, height=400, background_color=\"white\", colormap=\"summer\").generate(cleaned_pos)\n",
                "wc_neg = WordCloud(width=800, height=400, background_color=\"white\", colormap=\"autumn\").generate(cleaned_neg)\n",
                "\n",
                "fig, axes = plt.subplots(1, 2, figsize=(18, 8))\n",
                "axes[0].imshow(wc_pos, interpolation=\"bilinear\")\n",
                "axes[0].axis(\"off\")\n",
                "axes[0].set_title(\"Keywords in 5-Star Reviews\", fontsize=16, weight=\"bold\")\n",
                "\n",
                "axes[1].imshow(wc_neg, interpolation=\"bilinear\")\n",
                "axes[1].axis(\"off\")\n",
                "axes[1].set_title(\"Keywords in 1-Star Reviews\", fontsize=16, weight=\"bold\")\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. VADER Sentiment Scoring\n",
                "\n",
                "Let's see if VADER Sentiment Scores correlate well with review rating stars."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "analyzer = SentimentIntensityAnalyzer()\n",
                "\n",
                "sentiment_sample = reviews_sample.sample(10000, random_state=42).copy()\n",
                "sentiment_sample[\"vader_compound\"] = sentiment_sample[\"review_text\"].apply(lambda x: analyzer.polarity_scores(str(x))[\"compound\"])\n",
                "\n",
                "plt.figure(figsize=(10, 6))\n",
                "sns.boxplot(data=sentiment_sample, x=\"rating\", y=\"vader_compound\", palette=\"coolwarm\")\n",
                "plt.title(\"VADER Compound Sentiment Score by Star Rating\", fontsize=14, weight=\"bold\")\n",
                "plt.xlabel(\"Review Rating (Stars)\")\n",
                "plt.ylabel(\"VADER Compound Sentiment\")\n",
                "plt.show()"
            ]
        }
    ]
    create_notebook(cells, "notebooks/04_sentiment_nlp.ipynb")

def build_notebook_05():
    cells = [
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "# Sephora E-Commerce EDA: 05 - Business Insights & Value Mapping\n",
                "\n",
                "This final notebook synthesizes findings from both datasets to deliver business value: pricing indexing, uncovering highly-rated under-exposed products ('hidden gems'), and pointing out overrated luxury items."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "import sys\n",
                "import os\n",
                "sys.path.append(os.path.abspath(\"..\"))\n",
                "\n",
                "import pandas as pd\n",
                "import numpy as np\n",
                "import matplotlib.pyplot as plt\n",
                "import seaborn as sns\n",
                "\n",
                "from src.data_loader import load_products\n",
                "from src.viz_utils import set_custom_style\n",
                "\n",
                "set_custom_style()\n",
                "products_df = load_products(\"../data/product_info.csv\")"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 1. Value for Money Index\n",
                "\n",
                "We define a **Value Index** metric:  \n",
                "$$\\text{Value Index} = \\frac{\\text{Rating} \\times \\ln(\\text{Loves Count} + 1)}{\\text{Price (USD)}}$$\n",
                "This formula rewards high-quality (rating) products with strong social validation (loves count) relative to their price. We filter for items with reviews > 10 and price > 0."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "valid = products_df[(products_df[\"price_usd\"] > 0) & (products_df[\"reviews\"] > 10)].copy()\n",
                "valid[\"value_index\"] = (valid[\"rating\"] * np.log1p(valid[\"loves_count\"])) / valid[\"price_usd\"]\n",
                "\n",
                "top_value = valid.sort_values(by=\"value_index\", ascending=False).head(10)\n",
                "\n",
                "plt.figure(figsize=(12, 6))\n",
                "sns.barplot(data=top_value, x=\"value_index\", y=\"product_name\", palette=\"summer\")\n",
                "plt.title(\"Top 10 Sephora Value-for-Money Products\", fontsize=14, weight=\"bold\")\n",
                "plt.xlabel(\"Value for Money Index\")\n",
                "plt.ylabel(\"Product Name\")\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 2. Discovering 'Hidden Gems'\n",
                "\n",
                "These are products with ratings >= 4.5 and review counts between 10 and 50. They are exceptionally well-rated but haven't received enough reviews to go mainstream. Marketing could benefit from pushing these products."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "hidden_gems = products_df[\n",
                "    (products_df[\"rating\"] >= 4.5) & \n",
                "    (products_df[\"reviews\"] >= 10) & \n",
                "    (products_df[\"reviews\"] <= 50)\n",
                "].sort_values(by=\"loves_count\", ascending=False).head(10)\n",
                "\n",
                "plt.figure(figsize=(12, 6))\n",
                "sns.barplot(data=hidden_gems, x=\"loves_count\", y=\"product_name\", palette=\"viridis\")\n",
                "plt.title(\"Top 10 'Hidden Gems' in Sephora Catalog\", fontsize=14, weight=\"bold\")\n",
                "plt.xlabel(\"Loves Count (Engagement)\")\n",
                "plt.ylabel(\"Product Name\")\n",
                "plt.show()"
            ]
        },
        {
            "cell_type": "markdown",
            "metadata": {},
            "source": [
                "## 3. Identifying Overrated Luxury Products\n",
                "\n",
                "These are items with pricing >= $80, rating <= 3.5, and review count >= 30. Customers are paying premium luxury prices for products with demonstrably below-average ratings, signaling formulation or value problems."
            ]
        },
        {
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": [
                "overrated = products_df[\n",
                "    (products_df[\"price_usd\"] >= 80) & \n",
                "    (products_df[\"rating\"] <= 3.5) & \n",
                "    (products_df[\"reviews\"] >= 30)\n",
                "].sort_values(by=\"rating\", ascending=True).head(10)\n",
                "\n",
                "if len(overrated) > 0:\n",
                "    plt.figure(figsize=(12, 6))\n",
                "    sns.barplot(data=overrated, x=\"price_usd\", y=\"product_name\", palette=\"autumn\")\n",
                "    plt.title(\"Luxury Products with Poor Ratings (Price >= $80, Rating <= 3.5)\", fontsize=14, weight=\"bold\")\n",
                "    plt.xlabel(\"Price (USD)\")\n",
                "    plt.ylabel(\"Product Name\")\n",
                "    plt.show()\n",
                "else:\n",
                "    print(\"No overrated products found matching threshold.\")"
            ]
        }
    ]
    create_notebook(cells, "notebooks/05_business_insights.ipynb")

def build_all_notebooks():
    build_notebook_01()
    build_notebook_02()
    build_notebook_03()
    build_notebook_04()
    build_notebook_05()
    print("All notebooks created successfully in notebooks/!")

if __name__ == "__main__":
    build_all_notebooks()
