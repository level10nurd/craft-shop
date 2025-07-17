# 🎨 Craft Contemporary Analytics Dashboard

**MVP Proof of Concept** | **Museum Shop Business Intelligence**

A Streamlit dashboard providing business insights from Lightspeed POS data for Craft Contemporary museum shop.

## 🚀 Quick Deploy to Streamlit Cloud

1. **Fork/Clone** this repository to your GitHub account
2. **Go to** [share.streamlit.io](https://share.streamlit.io)
3. **Connect** your GitHub repository
4. **Set app path** to: `02-analytics-dashboard/streamlit_app.py`
5. **Add secrets** in Streamlit Cloud settings:
   ```toml
   SUPABASE_URL = "https://jzwkncthxjwqfzeztozm.supabase.co"
   SUPABASE_SERVICE_ROLE_KEY = "your-actual-key-here"
   ```

## 📊 Dashboard Features

### Key Metrics
- **30-Day Revenue** - Total sales for the period
- **Transaction Count** - Number of purchases
- **Average Transaction** - Per-purchase value
- **Daily Average** - Revenue per day

### Visualizations
- **Daily Sales Trend** - Revenue timeline over 30 days
- **Sales by Day of Week** - Visitor pattern analysis
- **Top Selling Products** - Best performers by quantity
- **Revenue by Product** - Highest earning items

### Business Insights
- Revenue patterns and performance highlights
- Peak business days and visitor trends
- Product performance analysis
- Actionable insights for museum shop management

## 🛠 Local Development

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally
streamlit run src/main.py
```

## 🔧 Configuration

The dashboard automatically detects deployment environment:
- **Local**: Uses `.env.local` file
- **Cloud**: Uses Streamlit Cloud secrets

## 🎯 Use Cases

Perfect for:
- **Executive Director** - High-level business overview
- **Museum Shop Manager** - Operational insights
- **Board Presentations** - Performance reporting
- **Strategic Planning** - Data-driven decisions

## 📈 Data Source

Connects to synchronized Lightspeed Retail POS data via Supabase:
- Real sales transactions
- Product catalog information
- Customer purchase patterns
- Inventory insights

*Data updates automatically from daily sync process*

---

**Built for**: Craft Contemporary Museum Shop  
**Purpose**: Proof of concept business intelligence  
**Technology**: Streamlit + Supabase + Plotly