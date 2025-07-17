

import os
import csv
from dotenv import load_dotenv
from lightspeed_x import LightspeedX

load_dotenv()

lightspeed = LightspeedX(
    base_url=os.getenv("base_url"),
    bearer_token=os.getenv("bearer_token"),
)

start_date = "2024-07-01T00:00:00Z"
end_date = "2025-06-30T23:59:59Z"

all_sales_data = []
offset = 0
limit = 100  # Max records per page

print("Fetching sales data from Lightspeed API...")

while True:
    params = {
        "timeStamp": f">=,{start_date},<=,{end_date}",
        "limit": limit,
        "offset": offset
    }
    
    response = lightspeed.get("2.0/sales", params=params)
    
    if not response or not response.get("data"):
        break
        
    data = response["data"]
    all_sales_data.extend(data)

    print(f"Retrieved {len(data)} records, total so far: {len(all_sales_data)}")

    if len(data) < limit:
        break  # Last page reached
    
    offset += limit

print("Finished fetching data. Processing sales by SKU...")

sales_by_sku = {}

for sale in all_sales_data:
    for item in sale.get("line_items", []):
        sku = item.get("product_id")
        if sku:
            total_price = float(item.get("price_total", 0.0))
            sales_by_sku.setdefault(sku, 0.0)
            sales_by_sku[sku] += total_price

report_filename = "sales_by_sku_report.csv"
with open(report_filename, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['SKU', 'Total Sales'])
    # Sort by SKU for consistent output
    for sku, total_sales in sorted(sales_by_sku.items()):
        writer.writerow([sku, f"{total_sales:.2f}"])

print(f"\nReport successfully saved to: {report_filename}")
