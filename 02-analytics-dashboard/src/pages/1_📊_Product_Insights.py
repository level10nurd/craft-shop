import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from main import init_supabase

st.set_page_config(
    page_title="Product Insights - Craft Contemporary",
    page_icon="📊",
    layout="wide"
)

@st.cache_data(ttl=300)
def load_products_with_sales(date_from, date_to):
    """Load comprehensive product performance data"""
    try:
        supabase = init_supabase()
        
        # Load sales in date range
        sales_response = supabase.table("lightspeed_sales")\
            .select("*")\
            .gte("sale_date", date_from)\
            .lte("sale_date", date_to)\
            .execute()
        sales_df = pd.DataFrame(sales_response.data)
        
        if sales_df.empty:
            return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()
        
        # Load line items for these sales
        sale_ids = sales_df['id'].tolist()
        line_items_data = []
        
        # Batch query line items (Supabase has limits on IN queries)
        batch_size = 50
        for i in range(0, len(sale_ids), batch_size):
            batch_ids = sale_ids[i:i+batch_size]
            response = supabase.table("lightspeed_sale_line_items")\
                .select("*")\
                .in_("sale_id", batch_ids)\
                .execute()
            line_items_data.extend(response.data)
        
        line_items_df = pd.DataFrame(line_items_data)
        
        # Load all products
        products_response = supabase.table("lightspeed_products")\
            .select("*")\
            .execute()
        products_df = pd.DataFrame(products_response.data)
        
        return sales_df, line_items_df, products_df
        
    except Exception as e:
        st.error(f"Error loading product data: {e}")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

def main():
    st.title("📊 Product Performance Deep Dive")
    st.markdown("### Comprehensive Product Analytics")
    
    # Date range selector
    col1, col2, col3 = st.columns([1, 1, 2])
    
    with col1:
        date_from = st.date_input(
            "From Date",
            value=datetime.now() - timedelta(days=30),
            max_value=datetime.now().date()
        )
    
    with col2:
        date_to = st.date_input(
            "To Date",
            value=datetime.now().date(),
            max_value=datetime.now().date()
        )
    
    with col3:
        st.markdown(f"**Analysis Period**: {(date_to - date_from).days} days")
    
    # Load data
    sales_df, line_items_df, products_df = load_products_with_sales(
        date_from.strftime('%Y-%m-%d'),
        date_to.strftime('%Y-%m-%d')
    )
    
    if line_items_df.empty or products_df.empty:
        st.warning("No data available for the selected date range.")
        return
    
    # Merge line items with product info
    line_items_df['product_id'] = line_items_df['product_id'].astype(str)
    products_df['id'] = products_df['id'].astype(str)
    
    product_sales = line_items_df.merge(
        products_df[['id', 'name', 'sku', 'price', 'cost']],
        left_on='product_id',
        right_on='id',
        how='left'
    )
    
    st.markdown("---")
    
    # Product Performance Metrics
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🏆 Top Products by Revenue")
        
        if not product_sales.empty:
            # Calculate revenue by product
            product_sales['revenue'] = pd.to_numeric(product_sales['price_total'], errors='coerce').fillna(0)
            revenue_by_product = product_sales.groupby('name')['revenue'].sum().sort_values(ascending=False).head(15)
            
            fig = px.bar(
                x=revenue_by_product.values,
                y=revenue_by_product.index,
                orientation='h',
                title="Top 15 Products by Revenue",
                labels={'x': 'Revenue ($)', 'y': 'Product'}
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("📦 Top Products by Units Sold")
        
        if not product_sales.empty:
            # Calculate quantity by product
            product_sales['quantity'] = pd.to_numeric(product_sales['quantity'], errors='coerce').fillna(0)
            quantity_by_product = product_sales.groupby('name')['quantity'].sum().sort_values(ascending=False).head(15)
            
            fig = px.bar(
                x=quantity_by_product.values,
                y=quantity_by_product.index,
                orientation='h',
                title="Top 15 Products by Units Sold",
                labels={'x': 'Units Sold', 'y': 'Product'},
                color_discrete_sequence=['#FF6B6B']
            )
            fig.update_layout(height=600)
            st.plotly_chart(fig, use_container_width=True)
    
    # Product Profitability Analysis
    st.markdown("---")
    st.subheader("💰 Product Profitability Analysis")
    
    if 'cost' in product_sales.columns and 'price' in product_sales.columns:
        # Calculate profit margins
        product_sales['cost'] = pd.to_numeric(product_sales['cost'], errors='coerce').fillna(0)
        product_sales['price'] = pd.to_numeric(product_sales['price'], errors='coerce').fillna(0)
        
        # Group by product for profitability
        profitability = product_sales.groupby('name').agg({
            'revenue': 'sum',
            'quantity': 'sum',
            'cost': 'first',
            'price': 'first'
        }).reset_index()
        
        # Calculate metrics
        profitability['total_cost'] = profitability['cost'] * profitability['quantity']
        profitability['gross_profit'] = profitability['revenue'] - profitability['total_cost']
        profitability['margin_percent'] = (profitability['gross_profit'] / profitability['revenue'] * 100).round(1)
        
        # Filter out products with no sales
        profitability = profitability[profitability['revenue'] > 0].sort_values('gross_profit', ascending=False).head(20)
        
        # Create profitability scatter plot
        fig = px.scatter(
            profitability,
            x='revenue',
            y='margin_percent',
            size='quantity',
            hover_data=['name', 'gross_profit'],
            title="Product Profitability Matrix",
            labels={'revenue': 'Total Revenue ($)', 'margin_percent': 'Profit Margin (%)'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
    
    # Detailed Product Table
    st.markdown("---")
    st.subheader("📋 Detailed Product Performance")
    
    if not product_sales.empty:
        # Create summary table
        product_summary = product_sales.groupby(['name', 'sku']).agg({
            'quantity': 'sum',
            'revenue': 'sum',
            'sale_id': 'count'
        }).reset_index()
        
        product_summary.columns = ['Product', 'SKU', 'Units Sold', 'Revenue', 'Transactions']
        product_summary['Avg Transaction Size'] = (product_summary['Revenue'] / product_summary['Transactions']).round(2)
        product_summary = product_summary.sort_values('Revenue', ascending=False)
        
        # Format currency columns
        product_summary['Revenue'] = product_summary['Revenue'].apply(lambda x: f"${x:,.2f}")
        product_summary['Avg Transaction Size'] = product_summary['Avg Transaction Size'].apply(lambda x: f"${x:,.2f}")
        
        st.dataframe(
            product_summary,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Units Sold": st.column_config.NumberColumn(format="%d"),
                "Transactions": st.column_config.NumberColumn(format="%d")
            }
        )
    
    # Product Trends
    st.markdown("---")
    st.subheader("📈 Product Sales Trends")
    
    # Allow selection of top products to track
    if not product_sales.empty:
        top_products = revenue_by_product.head(10).index.tolist()
        selected_products = st.multiselect(
            "Select products to track",
            options=top_products,
            default=top_products[:5]
        )
        
        if selected_products:
            # Merge with sales dates
            product_trends = product_sales[product_sales['name'].isin(selected_products)].merge(
                sales_df[['id', 'sale_date']],
                left_on='sale_id',
                right_on='id',
                how='left'
            )
            
            product_trends['sale_date'] = pd.to_datetime(product_trends['sale_date'])
            daily_product_sales = product_trends.groupby([product_trends['sale_date'].dt.date, 'name'])['revenue'].sum().reset_index()
            
            fig = px.line(
                daily_product_sales,
                x='sale_date',
                y='revenue',
                color='name',
                title="Daily Revenue by Product",
                labels={'sale_date': 'Date', 'revenue': 'Revenue ($)', 'name': 'Product'}
            )
            fig.update_layout(height=400)
            st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()