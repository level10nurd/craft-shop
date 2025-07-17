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
def load_sales_data(date_from, date_to):
    """Load sales data with caching"""
    try:
        supabase = init_supabase()
        response = supabase.table("lightspeed_sales")\
            .select("*")\
            .gte("sale_date", date_from)\
            .lte("sale_date", date_to)\
            .execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error loading sales data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_product_data():
    """Load product data with caching"""
    try:
        supabase = init_supabase()
        response = supabase.table("lightspeed_products")\
            .select("*")\
            .execute()
        return pd.DataFrame(response.data)
    except Exception as e:
        st.error(f"Error loading product data: {e}")
        return pd.DataFrame()

@st.cache_data(ttl=300)
def load_sales_with_products(date_from, date_to):
    """Load sales line items with product details"""
    try:
        supabase = init_supabase()
        
        # First get sales in date range
        sales_response = supabase.table("lightspeed_sales")\
            .select("id")\
            .gte("sale_date", date_from)\
            .lte("sale_date", date_to)\
            .execute()
        
        if not sales_response.data:
            return pd.DataFrame()
        
        sale_ids = [sale['id'] for sale in sales_response.data]
        
        # Get line items for these sales (in batches due to query limits)
        all_line_items = []
        batch_size = 50
        
        for i in range(0, len(sale_ids), batch_size):
            batch_ids = sale_ids[i:i+batch_size]
            response = supabase.table("lightspeed_sale_line_items")\
                .select("*, product_id")\
                .in_("sale_id", batch_ids)\
                .execute()
            all_line_items.extend(response.data)
        
        # Get product details separately
        line_items_df = pd.DataFrame(all_line_items)
        if line_items_df.empty:
            return pd.DataFrame()
            
        # Get unique product IDs
        product_ids = line_items_df['product_id'].dropna().unique().tolist()
        
        # Fetch product details
        products_data = []
        for i in range(0, len(product_ids), batch_size):
            batch_product_ids = product_ids[i:i+batch_size]
            response = supabase.table("lightspeed_products")\
                .select("id, name, price")\
                .in_("id", batch_product_ids)\
                .execute()
            products_data.extend(response.data)
        
        products_df = pd.DataFrame(products_data)
        
        # Merge line items with products
        if not products_df.empty:
            line_items_df = line_items_df.merge(
                products_df,
                left_on='product_id',
                right_on='id',
                how='left',
                suffixes=('', '_product')
            )
        
        return line_items_df
        
    except Exception as e:
        st.error(f"Error loading sales with products: {e}")
        return pd.DataFrame()

def main():
    # Header
    st.title("🎨 Craft Contemporary Museum Shop")
    st.markdown("### Business Analytics Dashboard")
    
    # Sidebar for date filtering
    st.sidebar.header("📅 Date Range Filter")
    
    # Date range selection
    date_range = st.sidebar.selectbox(
        "Select period",
        ["Last 7 days", "Last 30 days", "Last 90 days", "Custom range"]
    )
    
    if date_range == "Custom range":
        col1, col2 = st.sidebar.columns(2)
        with col1:
            date_from = st.date_input("From", value=datetime.now() - timedelta(days=30))
        with col2:
            date_to = st.date_input("To", value=datetime.now())
    else:
        date_to = datetime.now().date()
        if date_range == "Last 7 days":
            date_from = date_to - timedelta(days=7)
        elif date_range == "Last 30 days":
            date_from = date_to - timedelta(days=30)
        else:  # Last 90 days
            date_from = date_to - timedelta(days=90)
    
    # Display selected range
    st.sidebar.info(f"**Showing data from:**\n{date_from} to {date_to}")
    
    st.markdown("---")
    
    # Load data
    sales_df = load_sales_data(date_from.strftime('%Y-%m-%d'), date_to.strftime('%Y-%m-%d'))
    products_df = load_product_data()
    
    if sales_df.empty:
        st.warning(f"No sales data available from {date_from} to {date_to}.")
        return
    
    # Convert sale_date to datetime
    sales_df['sale_date'] = pd.to_datetime(sales_df['sale_date'])
    sales_df['total_price'] = pd.to_numeric(sales_df['total_price'], errors='coerce').fillna(0)
    
    # Key Metrics Row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_revenue = sales_df['total_price'].sum()
        st.metric("Total Revenue", f"${total_revenue:,.2f}")
    
    with col2:
        total_transactions = len(sales_df)
        st.metric("Transactions", f"{total_transactions:,}")
    
    with col3:
        avg_transaction = total_revenue / total_transactions if total_transactions > 0 else 0
        st.metric("Avg Transaction", f"${avg_transaction:.2f}")
    
    with col4:
        # Calculate daily average
        days_in_range = (date_to - date_from).days + 1
        daily_avg = total_revenue / days_in_range if days_in_range > 0 else 0
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
                     title=f"Daily Revenue ({date_from} to {date_to})")
        fig.update_layout(height=400)
        fig.update_traces(line_color='#1f77b4', line_width=2)
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
                    title="Revenue by Day of Week",
                    color='total_price',
                    color_continuous_scale='Blues')
        fig.update_layout(height=400, showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    # Product Insights
    st.markdown("---")
    
    # Load line items for product analysis
    line_items_df = load_sales_with_products(date_from.strftime('%Y-%m-%d'), date_to.strftime('%Y-%m-%d'))
    
    if not line_items_df.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🏆 Top Selling Products")
            
            # Extract product names and calculate quantities
            if 'name' in line_items_df.columns:
                line_items_df['quantity'] = pd.to_numeric(line_items_df['quantity'], errors='coerce').fillna(0)
                top_products = line_items_df.groupby('name')['quantity'].sum().sort_values(ascending=False).head(10)
                
                fig = px.bar(
                    y=top_products.index,
                    x=top_products.values,
                    orientation='h',
                    title="Top 10 Products by Units Sold",
                    labels={'x': 'Units Sold', 'y': ''}
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Product details not available")
        
        with col2:
            st.subheader("💰 Revenue by Product")
            
            # Calculate revenue per product
            if 'name' in line_items_df.columns:
                line_items_df['price_total'] = pd.to_numeric(line_items_df['price_total'], errors='coerce').fillna(0)
                top_revenue = line_items_df.groupby('name')['price_total'].sum().sort_values(ascending=False).head(10)
                
                fig = px.bar(
                    y=top_revenue.index,
                    x=top_revenue.values,
                    orientation='h',
                    title="Top 10 Products by Revenue",
                    labels={'x': 'Revenue ($)', 'y': ''},
                    color_discrete_sequence=['#ff7f0e']
                )
                fig.update_layout(height=400)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Product revenue data not available")
    
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
            st.success(f"📅 **Peak Day**: {peak_dow['day_of_week']} typically sees highest sales")
        
        st.info(f"🛍️ **Average Purchase**: Visitors spend ${avg_transaction:.2f} per transaction")
    
    # Navigation hint
    st.markdown("---")
    st.info("💡 **Tip**: Visit the **📊 Product Insights** page in the sidebar for detailed product performance analysis!")
    
    # Footer
    st.markdown("---")
    st.markdown(f"*Data from {date_from} to {date_to} | Refreshed every 5 minutes*")

if __name__ == "__main__":
    main()