import os
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.io as pio

# Sephora-inspired Color Palette
# Crimson Red (#FF3366), Charcoal Black (#1A1A1A), Light Gray (#F5F5F5), Slate Gray (#7F8C8D), Pink Accent (#FF85A2)
SEPHORA_PALETTE = ["#FF3366", "#1A1A1A", "#3498DB", "#2ECC71", "#9B59B6", "#F1C40F", "#E67E22"]
SEPHORA_GRADIENT = sns.blend_palette(["#1A1A1A", "#FF3366"], as_cmap=True)

def set_custom_style():
    """
    Sets custom matplotlib and seaborn styles for a clean, premium, modern aesthetic.
    """
    sns.set_theme(style="whitegrid")
    
    # Custom matplotlib parameters
    plt.rcParams["figure.figsize"] = (10, 6)
    plt.rcParams["axes.facecolor"] = "#FAFAFA"
    plt.rcParams["axes.edgecolor"] = "#E0E0E0"
    plt.rcParams["axes.grid"] = True
    plt.rcParams["grid.color"] = "#EBEBEB"
    plt.rcParams["grid.linestyle"] = "--"
    plt.rcParams["axes.labelsize"] = 12
    plt.rcParams["axes.titlesize"] = 14
    plt.rcParams["axes.titleweight"] = "bold"
    plt.rcParams["xtick.labelsize"] = 10
    plt.rcParams["ytick.labelsize"] = 10
    plt.rcParams["font.sans-serif"] = ["DejaVu Sans", "Arial", "sans-serif"]
    plt.rcParams["font.family"] = "sans-serif"
    
    # Set default palette
    sns.set_palette(SEPHORA_PALETTE)
    
    # Plotly template
    pio.templates.default = "plotly_white"
    
    print("Custom plotting style and palettes configured successfully.")

def get_sephora_colors():
    """
    Returns the custom Sephora-themed colors dict.
    """
    return {
        "primary": "#FF3366",
        "dark": "#1A1A1A",
        "blue": "#3498DB",
        "green": "#2ECC71",
        "purple": "#9B59B6",
        "yellow": "#F1C40F",
        "orange": "#E67E22",
        "light_gray": "#F5F5F5"
    }

def save_figure(fig, filename, folder="reports/figures"):
    """
    Saves a matplotlib figure as a high-resolution PNG file.
    
    Parameters:
    -----------
    fig : matplotlib.figure.Figure
        The figure object to save.
    filename : str
        The filename (e.g. 'price_distribution.png').
    folder : str
        Target folder to save the figure.
    """
    if not os.path.exists(folder):
        os.makedirs(folder, exist_ok=True)
        
    filepath = os.path.join(folder, filename)
    fig.savefig(filepath, dpi=300, bbox_inches="tight")
    print(f"Figure saved successfully to {filepath}")

def plot_bar_ranking(data, x, y, title, xlabel="", ylabel="", top_n=10, palette=None, filename=None):
    """
    Generates and saves a clean, sorted horizontal bar plot.
    """
    fig, ax = plt.subplots(figsize=(12, 6))
    
    # Sort data
    sorted_data = data.sort_values(by=x, ascending=False).head(top_n)
    
    # Select palette
    if palette is None:
        palette = sns.blend_palette(["#FF85A2", "#FF3366"], n_colors=top_n)
        
    sns.barplot(
        data=sorted_data,
        x=x,
        y=y,
        palette=palette,
        ax=ax
    )
    
    ax.set_title(title, pad=15)
    ax.set_xlabel(xlabel or x, labelpad=10)
    ax.set_ylabel(ylabel or y, labelpad=10)
    
    sns.despine(left=True, bottom=True)
    
    if filename:
        save_figure(fig, filename)
        
    plt.show()
    plt.close()
