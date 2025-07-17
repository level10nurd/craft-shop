import streamlit as st
import os
from dotenv import load_dotenv
from supabase import create_client
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

# Load environment variables - try multiple sources for local vs cloud deployment
try:
    load_dotenv("../../.env.local")  # Local development
except:
    load_dotenv(".env.local")  # Alternative local path
    
# For Streamlit Cloud, use st.secrets
SUPABASE_URL = os.getenv("SUPABASE_URL") or st.secrets.get("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY") or st.secrets.get("SUPABASE_SERVICE_ROLE_KEY")

st.set_page_config(
    page_title="Craft Contemporary Analytics",
    page_icon="🎨",
    layout="wide"
)


@st.cache_resource
def init_supabase():
    """Initialize Supabase client with caching"""
    if not SUPABASE_URL or not SUPABASE_KEY:
        st.error("Missing Supabase configuration.")
        st.stop()
    return create_client(SUPABASE_URL, SUPABASE_KEY)

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_sales_data(supabase):
    """Load sales data with caching"""
    try:
        thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        response = supabase.table("lightspeed_sales")\
            .select("*")\
            .gte("sale_date", thirty_days_ago)\
            .execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error loading sales data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_product_data(supabase):
    """Load product data with caching"""
    try:
        response = supabase.table("lightspeed_products")\
            .select("*")\
            .execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error loading product data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_sales_with_products(supabase):
    """Load sales line items with product details"""
    try:
        response = supabase.table("lightspeed_sale_line_items")\
            .select("*, lightspeed_products(name, price)")\
            .execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error loading sales with products: {e}")
        return pd.DataFrame()

def main():
    supabase = init_supabase()
    
    # Header
    st.title("🎨 Craft Contemporary Museum Shop")
    st.markdown("### Business Analytics Dashboard")
    st.markdown("---")
    
    # Load data
    sales_df = load_sales_data(supabase)
    products_df = load_product_data(supabase)
    
    if sales_df.empty:
        st.warning("No sales data available for the last 30 days.")
        return
    
    # Convert sale_date to datetime
    sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'])
    sales_df['total_price'] = pd.to_numeric(sales_df['total_price'], errors='coerce').fillna(0)
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = sales_df['total_price'].sum()
        st.metric("30-Day Revenue", f"${total_revenue:,.2f}")
    
    with col2:
        total_transactions = len(sales_df)
        st.metric("Transactions", f"{total_transactions:,}")
    
    with col3:
        avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0
        st.metric("Avg Transaction", f"${avg_transaction:.2f}")
    
    with col4:
        # Calculate daily average
        daily_avg = total_revenue / 30
        st.metric("Daily Average", f"${daily_avg:.2f}")
    
    st.markdown("---")
    
    # Charts Row 1
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Daily Sales Trend")
        # Group by date and sum sales
        daily_sales = sales_df.groupby(sales_df['sale_date'].dt.date)['total_price'].sum().reset_index()
        daily_sales.columns = ['Date', 'Revenue']
        
        fig = px.line(daily_sales, x='Date', y='Revenue', 
                     title="Daily Revenue Over Last 30 Days")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📊 Sales by Day of Week")
        # Add day of week
        sales_df['day_of_week'] = sales_df['sale_date'].dt.day_name()
        dow_sales = sales_df.groupby('day_of_week')['total_price'].sum().reset_index()
        
        # Order days properly
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        dow_sales['day_of_week'] = pd.Categorical(dow_sales['day_of_week'], categories=day_order, ordered=True)
        dow_sales = dow_sales.sort_values('day_of_week')
        
        fig = px.bar(dow_sales, x='day_of_week', y='total_price',
                    title="Revenue by Day of Week")
        fig.update_layout(height=400)
        st.plotly_chart(fig, use_container_width=True)
    
    # Product Insights
    st.markdown("---")
    
    # Load line items for product analysis
    line_items_df = load_sales_with_products(supabase)
    
    if not line_items_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top Selling Products")
            
            # Extract product names and calculate quantities
            product_sales = []
            for _, row in line_items_df.iterrows():
                if row['lightspeed_products']:
                    product_name = row['lightspeed_products']['name']
                    quantity = float(row.get('quantity', 0))
                    product_sales.append({'Product': product_name, 'Quantity': quantity})
            
            if product_sales:
                products_summary = pd.DataFrame(product_sales)
                top_products = products_summary.groupby('Product')['Quantity'].sum().sort_values(ascending=False).head(10)
                
                st.bar_chart(top_products)
            else:
                st.info("No product sales data available")
        
        with col2:
            st.subheader("💰 Revenue by Product")
            
            # Calculate revenue per product
            product_revenue = []
            for _, row in line_items_df.iterrows():
                if row['lightspeed_products']:
                    product_name = row['lightspeed_products']['name']
                    price = float(row.get('price_total', 0))
                    product_revenue.append({'Product': product_name, 'Revenue': price})
            
            if product_revenue:
                revenue_summary = pd.DataFrame(product_revenue)
                top_revenue = revenue_summary.groupby('Product')['Revenue'].sum().sort_values(ascending=False).head(10)
                
                st.bar_chart(top_revenue)
            else:
                st.info("No product revenue data available")
    
    # Business Insights
    st.markdown("---")
    st.subheader("📋 Business Insights")
    
    insights_col1, insights_col2 = st.columns(2)
    
    with insights_col1:
        st.info(f"💡 **Revenue Pattern**: ${total_revenue:,.0f} generated from {total_transactions} transactions")
        
        # Find busiest day
        if not daily_sales.empty:
            best_day = daily_sales.loc[daily_sales['Revenue'].idxmax()]
            st.success(f"🎯 **Best Day**: {best_day['Date']} with ${best_day['Revenue']:.2f}")
    
    with insights_col2:
        # Find peak day of week
        if not dow_sales.empty:
            peak_dow = dow_sales.loc[dow_sales['total_price'].idxmax()]
            st.success(f"📅 **Peak Day**: {peak_dow['day_of_week']} averages ${peak_dow['total_price']:.2f}")
        
        st.info(f"🛍️ **Average Purchase**: Visitors spend ${avg_transaction:.2f} per transaction")
    
    # Footer
    st.markdown("---")
    st.markdown("*Data refreshed every 5 minutes | Last 30 days of activity*")

if __name__ == "__main__":
    main()