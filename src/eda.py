import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def run_eda():
    print("Initializing Exploratory Data Analysis (EDA) Pipeline...")
    processed_dir = os.path.join("data", "processed")
    images_dir = "images"
    os.makedirs(images_dir, exist_ok=True)
    
    # Set professional plotting style
    sns.set_theme(style="whitegrid")
    plt.rcParams.update({
        'font.size': 10,
        'axes.labelsize': 12,
        'axes.titlesize': 14,
        'xtick.labelsize': 10,
        'ytick.labelsize': 10,
        'figure.titlesize': 16,
        'figure.dpi': 150
    })
    
    # Load processed datasets
    df_suppliers = pd.read_csv(os.path.join(processed_dir, "suppliers.csv"))
    df_warehouses = pd.read_csv(os.path.join(processed_dir, "warehouses.csv"))
    df_products = pd.read_csv(os.path.join(processed_dir, "products.csv"))
    df_sales = pd.read_csv(os.path.join(processed_dir, "sales.csv"))
    df_inventory = pd.read_csv(os.path.join(processed_dir, "inventory.csv"))
    
    # Merge Sales with Products and Warehouses for enriched analysis
    df_sales_enriched = df_sales.merge(df_products, on="product_id", how="left")
    df_sales_enriched = df_sales_enriched.merge(df_warehouses, on="warehouse_id", how="left")
    
    # ------------------ Plot 1: Monthly Sales Revenue Trend ------------------
    print("Generating Plot 1: Monthly Sales Revenue Trend...")
    df_sales_enriched["sale_date"] = pd.to_datetime(df_sales_enriched["sale_date"])
    df_sales_enriched["year_month"] = df_sales_enriched["sale_date"].dt.to_period("M")
    
    monthly_sales = df_sales_enriched.groupby("year_month")["revenue"].sum().reset_index()
    monthly_sales["year_month"] = monthly_sales["year_month"].astype(str)
    
    plt.figure(figsize=(10, 5))
    sns.lineplot(data=monthly_sales, x="year_month", y="revenue", marker="o", color="#1f77b4", linewidth=2.5)
    plt.fill_between(monthly_sales["year_month"], monthly_sales["revenue"], color="#1f77b4", alpha=0.1)
    plt.title("Monthly Revenue Trend (1-Year Period)", pad=15)
    plt.xlabel("Month")
    plt.ylabel("Revenue ($)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "monthly_sales_trend.png"))
    plt.close()
    
    # ------------------ Plot 2: Category Sales Revenue (Pareto Chart) ------------------
    print("Generating Plot 2: Category Sales Pareto...")
    cat_sales = df_sales_enriched.groupby("category")["revenue"].sum().sort_values(ascending=False).reset_index()
    cat_sales["cum_pct"] = (cat_sales["revenue"].cumsum() / cat_sales["revenue"].sum()) * 100
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    
    # Bar chart for category revenue
    sns.barplot(data=cat_sales, x="category", y="revenue", ax=ax1, palette="Blues_r")
    ax1.set_ylabel("Revenue ($)", color="#1f77b4")
    ax1.tick_params(axis='y', labelcolor="#1f77b4")
    ax1.set_xlabel("Product Category")
    ax1.set_title("Revenue Contribution by Product Category (Pareto Chart)", pad=15)
    
    # Line chart for cumulative percentage
    ax2 = ax1.twinx()
    ax2.plot(cat_sales["category"], cat_sales["cum_pct"], color="#d62728", marker="D", ms=7, linewidth=2, label="Cumulative %")
    ax2.set_ylabel("Cumulative Percentage (%)", color="#d62728")
    ax2.tick_params(axis='y', labelcolor="#d62728")
    ax2.set_ylim(0, 110)
    
    # Add 80% cut-off line
    ax2.axhline(80, color="gray", linestyle="--", alpha=0.7)
    ax2.text(0, 82, "80% Cutoff", color="gray", fontsize=10)
    
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "category_pareto_chart.png"))
    plt.close()
    
    # ------------------ Plot 3: Warehouse Sales Distribution ------------------
    print("Generating Plot 3: Warehouse Sales Performance...")
    wh_sales = df_sales_enriched.groupby("warehouse_name")["revenue"].sum().sort_values(ascending=False).reset_index()
    
    plt.figure(figsize=(8, 5))
    sns.barplot(data=wh_sales, x="warehouse_name", y="revenue", palette="viridis")
    plt.title("Revenue Contribution by Warehouse Hub", pad=15)
    plt.xlabel("Warehouse Name")
    plt.ylabel("Gross Revenue ($)")
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "warehouse_performance.png"))
    plt.close()
    
    # ------------------ Plot 4: Product Unit Price Distribution ------------------
    print("Generating Plot 4: Product Price Distribution...")
    plt.figure(figsize=(8, 5))
    sns.histplot(data=df_products, x="unit_price", kde=True, bins=30, color="#2ca02c")
    plt.title("Distribution of Product Unit Prices", pad=15)
    plt.xlabel("Unit Price ($)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "product_price_distribution.png"))
    plt.close()
    
    # ------------------ Plot 5: Correlation Matrix ------------------
    print("Generating Plot 5: Correlation Matrix...")
    numeric_cols = ["unit_price", "unit_cost", "lead_time_days", "min_order_qty"]
    corr = df_products[numeric_cols].corr()
    
    plt.figure(figsize=(7, 5))
    sns.heatmap(corr, annot=True, cmap="coolwarm", fmt=".2f", linewidths=0.5, vmin=-1, vmax=1)
    plt.title("Correlation Matrix of Product Variables", pad=15)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "correlation_matrix.png"))
    plt.close()
    
    # ------------------ Plot 6: Outlier Detection in Sales Quantities ------------------
    print("Generating Plot 6: Boxplot of Sales Quantities...")
    plt.figure(figsize=(8, 4))
    sns.boxplot(data=df_sales, x="quantity_sold", color="#e377c2")
    plt.title("Outlier Detection in Order Quantities", pad=15)
    plt.xlabel("Quantity Sold per Transaction")
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "sales_qty_outliers.png"))
    plt.close()
    
    # ------------------ Plot 7: Supplier Performance Scatter ------------------
    print("Generating Plot 7: Supplier Reliability vs Rating...")
    plt.figure(figsize=(8, 5))
    sns.scatterplot(data=df_suppliers, x="reliability_score", y="rating", size="rating", hue="rating", palette="crest", legend=False, sizes=(40, 240))
    plt.title("Supplier Profile: Reliability Score vs Rating", pad=15)
    plt.xlabel("Reliability Score (On-Time Delivery %)")
    plt.ylabel("Supplier Rating (1-5 Stars)")
    plt.xlim(0.70, 1.0)
    plt.ylim(2.5, 5.2)
    plt.tight_layout()
    plt.savefig(os.path.join(images_dir, "supplier_reliability_scatter.png"))
    plt.close()
    
    print("\nEDA completed. Plots saved to 'images/' folder:")
    print(" - monthly_sales_trend.png")
    print(" - category_pareto_chart.png")
    print(" - warehouse_performance.png")
    print(" - product_price_distribution.png")
    print(" - correlation_matrix.png")
    print(" - sales_qty_outliers.png")
    print(" - supplier_reliability_scatter.png")

if __name__ == "__main__":
    run_eda()
