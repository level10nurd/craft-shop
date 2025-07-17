#!/usr/bin/env python3
"""
Flask Sync Status Dashboard for Lightspeed to Supabase sync monitoring.
Simple dashboard showing sync health for all 6 entity types.
"""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, session, flash
from supabase import create_client, Client

# Load environment variables
load_dotenv('.env.local')

app = Flask(__name__)
app.secret_key = os.environ.get('DASHBOARD_SECRET_KEY', 'dev-secret-key-change-in-production')

# Supabase configuration
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") 
DASHBOARD_PASSWORD = os.environ.get("DASHBOARD_PASSWORD", "craft2025")

def get_supabase_client() -> Client:
    """Create Supabase client."""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def get_sync_status():
    """Fetch sync status for all entity types with health indicators."""
    supabase = get_supabase_client()
    
    # Entity types we're monitoring
    entity_types = ['customers', 'outlets', 'products', 'sales', 'sale_line_items', 'inventory']
    
    status_data = []
    now = datetime.now()
    
    for entity_type in entity_types:
        try:
            # Try to get sync state from the table
            result = supabase.table('sync_state').select('*').eq('entity_type', entity_type).execute()
            
            if result.data:
                sync_data = result.data[0]
                last_sync = sync_data.get('last_sync_time')
                status = sync_data.get('status', 'unknown')
                error_message = sync_data.get('error_message')
                
                # Parse last sync time if it exists
                if last_sync:
                    last_sync_dt = datetime.fromisoformat(last_sync.replace('Z', '+00:00'))
                    time_diff = now - last_sync_dt.replace(tzinfo=None)
                    
                    # Determine health status based on time thresholds
                    if time_diff < timedelta(hours=2):
                        health = 'healthy'
                    elif time_diff < timedelta(hours=12):
                        health = 'warning'
                    else:
                        health = 'error'
                        
                    last_sync_display = last_sync_dt.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    health = 'error'
                    last_sync_display = 'Never'
                    
            else:
                # No sync state record found
                status = 'never_synced'
                health = 'error'
                last_sync_display = 'Never'
                error_message = 'No sync state record'
                
        except Exception as e:
            # Database connection or query error
            status = 'error'
            health = 'error'
            last_sync_display = 'Error'
            error_message = str(e)
            
        # Map entity types to friendly names and table names
        entity_info = {
            'customers': {'name': 'Customers', 'table': 'lightspeed_customers'},
            'outlets': {'name': 'Outlets', 'table': 'lightspeed_outlets'},
            'products': {'name': 'Products', 'table': 'lightspeed_products'},
            'sales': {'name': 'Sales', 'table': 'lightspeed_sales'},
            'sale_line_items': {'name': 'Sale Line Items', 'table': 'lightspeed_sale_line_items'},
            'inventory': {'name': 'Inventory', 'table': 'lightspeed_inventory'}
        }
        
        status_data.append({
            'entity_type': entity_type,
            'name': entity_info[entity_type]['name'],
            'table': entity_info[entity_type]['table'],
            'status': status,
            'health': health,
            'last_sync': last_sync_display,
            'error_message': error_message
        })
    
    return status_data

@app.route('/')
def home():
    """Redirect to dashboard if authenticated, otherwise show login."""
    if session.get('authenticated'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Simple password authentication for CFO access."""
    if request.method == 'POST':
        password = request.form.get('password')
        if password == DASHBOARD_PASSWORD:
            session['authenticated'] = True
            flash('Successfully logged in!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid password. Please try again.', 'error')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Main sync status dashboard."""
    if not session.get('authenticated'):
        flash('Please log in to access the dashboard.', 'error')
        return redirect(url_for('login'))
    
    try:
        status_data = get_sync_status()
        return render_template('dashboard.html', status_data=status_data)
    except Exception as e:
        flash(f'Error loading dashboard: {str(e)}', 'error')
        return render_template('dashboard.html', status_data=[], error=str(e))

@app.route('/logout')
def logout():
    """Log out and clear session."""
    session.pop('authenticated', None)
    flash('Successfully logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    try:
        supabase = get_supabase_client()
        # Simple connectivity test
        result = supabase.table('sync_state').select('entity_type').limit(1).execute()
        return {'status': 'healthy', 'database': 'connected'}, 200
    except Exception as e:
        return {'status': 'unhealthy', 'error': str(e)}, 500

if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5001)