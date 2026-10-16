import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Project folder location
BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "Online Retail.xlsx"
OUTPUT_DIR = BASE_DIR / "outputs"
OUTPUT_DIR.mkdir(exist_ok=True)

# 1. Load dataset
print("Loading dataset...")
df = pd.read_excel(DATA_FILE)

print("\nDataset loaded successfully!")
print("Total rows:", len(df))
print("\nFirst 5 records:")
print(df.head())

# 2. Data cleaning
df.columns = df.columns.str.strip()
df["InvoiceDate"] = pd.to_datetime(
    df["InvoiceDate"], errors="coerce"
)

cancelled = df["InvoiceNo"].astype(str).str.startswith("C")

df = df[
    ~cancelled
    & df["Description"].notna()
    & df["InvoiceDate"].notna()
    & (df["Quantity"] > 0)
    & (df["UnitPrice"] > 0)
].copy()

# 3. Calculate sales
df["Revenue"] = df["Quantity"] * df["UnitPrice"]
df["Month"] = df["InvoiceDate"].dt.to_period("M").astype(str)

print("\n--- SALES ANALYSIS REPORT ---")
print("Valid transactions:", len(df))
print(f"Total Revenue: £{df['Revenue'].sum():,.2f}")
print("Total Orders:", df["InvoiceNo"].nunique())
print("Total Items Sold:", df["Quantity"].sum())
print("Identified Customers:", df["CustomerID"].nunique())

# 4. Monthly revenue analysis
monthly_sales = df.groupby("Month")["Revenue"].sum()

print("\nMonthly Revenue:")
print(monthly_sales)

monthly_sales.to_csv(OUTPUT_DIR / "monthly_sales.csv")

plt.figure(figsize=(12, 6))
monthly_sales.plot(marker="o")
plt.title("Monthly Revenue Analysis")
plt.xlabel("Month")
plt.ylabel("Revenue (£)")
plt.xticks(rotation=45)
plt.grid(True, alpha=0.3)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "monthly_revenue.png")
plt.close()

# 5. Top 10 products
top_products = (
    df.groupby("Description")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\nTop 10 Products by Revenue:")
print(top_products)

top_products.to_csv(OUTPUT_DIR / "top_products.csv")

plt.figure(figsize=(10, 6))
top_products.sort_values().plot(kind="barh")
plt.title("Top 10 Products by Revenue")
plt.xlabel("Revenue (£)")
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "top_products.png")
plt.close()

# 6. Country-wise revenue
top_countries = (
    df.groupby("Country")["Revenue"]
    .sum()
    .sort_values(ascending=False)
    .head(10)
)

print("\nTop 10 Countries by Revenue:")
print(top_countries)

top_countries.to_csv(OUTPUT_DIR / "top_countries.csv")

# 7. Save cleaned dataset
df.to_csv(OUTPUT_DIR / "cleaned_data.csv", index=False)

# 8. Final result
print("\nAnalysis completed successfully!")
print("All reports and graphs are saved in the outputs folder.")
# 9. Customer Behaviour Analysis
print("\n--- CUSTOMER ANALYSIS ---")

# Keep records with a known CustomerID
customer_df = df.dropna(subset=["CustomerID"]).copy()

# Analyse each customer's purchases
customer_analysis = customer_df.groupby("CustomerID").agg(
    TotalOrders=("InvoiceNo", "nunique"),
    TotalItems=("Quantity", "sum"),
    TotalSpent=("Revenue", "sum")
).reset_index()

customer_analysis = customer_analysis.sort_values(
    "TotalSpent", ascending=False
)

print("\nTop 10 Customers by Spending:")
print(customer_analysis.head(10).to_string(index=False))

customer_analysis.to_csv(
    OUTPUT_DIR / "customer_analysis.csv", index=False
)

# Repeat customer analysis
repeat_customers = (
    customer_analysis["TotalOrders"] > 1
).sum()

total_customers = len(customer_analysis)

print("\nTotal Identified Customers:", total_customers)
print("Repeat Customers:", repeat_customers)

if total_customers > 0:
    repeat_rate = repeat_customers / total_customers * 100
    print(f"Repeat Customer Rate: {repeat_rate:.2f}%")

# Save top customer chart
top_customers = customer_analysis.head(10).copy()
top_customers["CustomerID"] = (
    top_customers["CustomerID"].astype(str)
)

plt.figure(figsize=(10, 6))
plt.bar(
    top_customers["CustomerID"],
    top_customers["TotalSpent"]
)
plt.title("Top 10 Customers by Total Spending")
plt.xlabel("Customer ID")
plt.ylabel("Total Spending (£)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(OUTPUT_DIR / "top_customers.png")
plt.close()

print("\nCustomer analysis completed!")