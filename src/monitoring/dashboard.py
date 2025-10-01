"""
Streamlit Dashboard for Fraud Detection API Monitoring

This dashboard provides real-time monitoring and analytics for the
fraud detection API, including prediction logs and performance metrics.
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from datetime import datetime, timedelta
import time
import os

# Page configuration
st.set_page_config(
    page_title="Fraud Detection Monitoring",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .fraud-alert {
        background-color: #ffebee;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #f44336;
    }
    .normal-alert {
        background-color: #e8f5e8;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #4caf50;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_prediction_logs():
    """Load prediction logs from CSV file"""
    log_file = "data/logs/predictions.csv"
    if os.path.exists(log_file):
        df = pd.read_csv(log_file)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        return df
    return pd.DataFrame()

def get_api_health():
    """Get API health status"""
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def get_api_metrics():
    """Get API metrics"""
    try:
        response = requests.get("http://localhost:8000/metrics", timeout=5)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return None

def test_prediction():
    """Send a test prediction to the API"""
    test_transaction = {
        "amount": 150.0,
        "merchant_category": "grocery",
        "transaction_type": "purchase",
        "location": "seattle_wa",
        "device_type": "mobile",
        "hour_of_day": 14,
        "day_of_week": 2,
        "user_transaction_frequency": 5.0,
        "user_avg_amount": 100.0,
        "user_transaction_count": 25
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/predict",
            json=test_transaction,
            timeout=10
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Test prediction failed: {str(e)}")
    return None

def main():
    """Main dashboard function"""
    
    # Title and header
    st.title("🛡️ Fraud Detection API Monitoring Dashboard")
    st.markdown("Real-time monitoring and analytics for fraud detection predictions")
    
    # Sidebar
    st.sidebar.header("🔧 Controls")
    
    # Auto-refresh toggle
    auto_refresh = st.sidebar.checkbox("Auto-refresh (30s)", value=False)
    
    # Manual refresh button
    if st.sidebar.button("🔄 Refresh Now"):
        st.rerun()
    
    # Test prediction button
    if st.sidebar.button("🧪 Send Test Prediction"):
        with st.spinner("Sending test prediction..."):
            result = test_prediction()
            if result:
                st.sidebar.success("✅ Test prediction successful")
                st.sidebar.json(result)
            else:
                st.sidebar.error("❌ Test prediction failed")
    
    # API Status Section
    st.header("📊 API Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Get API health and metrics
    health_data = get_api_health()
    metrics_data = get_api_metrics()
    
    with col1:
        if health_data:
            status = health_data.get('status', 'unknown')
            if status == 'healthy':
                st.success(f"🟢 API Status: {status.title()}")
            else:
                st.error(f"🔴 API Status: {status.title()}")
        else:
            st.error("🔴 API Status: Unreachable")
    
    with col2:
        if health_data:
            uptime = health_data.get('uptime_seconds', 0)
            uptime_str = str(timedelta(seconds=int(uptime)))
            st.info(f"⏱️ Uptime: {uptime_str}")
        else:
            st.info("⏱️ Uptime: Unknown")
    
    with col3:
        if metrics_data:
            total_pred = metrics_data.get('total_predictions', 0)
            st.info(f"📈 Total Predictions: {total_pred:,}")
        else:
            st.info("📈 Total Predictions: Unknown")
    
    with col4:
        if metrics_data:
            pred_per_sec = metrics_data.get('predictions_per_second', 0)
            st.info(f"⚡ Requests/sec: {pred_per_sec:.2f}")
        else:
            st.info("⚡ Requests/sec: Unknown")
    
    # Prediction Logs Section
    st.header("📋 Prediction Logs")
    
    # Load prediction data
    df = load_prediction_logs()
    
    if df.empty:
        st.warning("📭 No prediction logs found. Send some predictions to see data here.")
        st.info("💡 Use the 'Send Test Prediction' button in the sidebar to generate sample data.")
        return
    
    # Recent predictions summary
    col1, col2, col3, col4 = st.columns(4)
    
    # Filter to last 24 hours
    last_24h = df[df['timestamp'] > (datetime.now() - timedelta(hours=24))]
    
    with col1:
        total_predictions = len(last_24h)
        st.metric("Total Predictions (24h)", total_predictions)
    
    with col2:
        fraud_predictions = len(last_24h[last_24h['is_fraud'] == True])
        fraud_rate = (fraud_predictions / total_predictions * 100) if total_predictions > 0 else 0
        st.metric("Fraud Detected (24h)", fraud_predictions, f"{fraud_rate:.1f}%")
    
    with col3:
        if not last_24h.empty:
            avg_amount = last_24h['amount'].mean()
            st.metric("Avg Transaction Amount", f"${avg_amount:.2f}")
        else:
            st.metric("Avg Transaction Amount", "$0.00")
    
    with col4:
        if not last_24h.empty:
            avg_processing = last_24h['processing_time_ms'].mean()
            st.metric("Avg Processing Time", f"{avg_processing:.1f}ms")
        else:
            st.metric("Avg Processing Time", "0ms")
    
    # Charts Section
    st.header("📊 Analytics")
    
    # Create tabs for different views
    tab1, tab2, tab3, tab4 = st.tabs(["📈 Time Series", "🎯 Risk Distribution", "💰 Amount Analysis", "⚡ Performance"])
    
    with tab1:
        if not df.empty:
            # Time series of predictions
            df_hourly = df.set_index('timestamp').resample('1H').agg({
                'is_fraud': ['count', 'sum'],
                'fraud_probability': 'mean'
            }).round(3)
            
            df_hourly.columns = ['total_predictions', 'fraud_count', 'avg_fraud_prob']
            df_hourly = df_hourly.reset_index()
            
            fig = make_subplots(
                rows=2, cols=1,
                subplot_titles=('Predictions per Hour', 'Average Fraud Probability'),
                vertical_spacing=0.1
            )
            
            # Predictions count
            fig.add_trace(
                go.Scatter(
                    x=df_hourly['timestamp'],
                    y=df_hourly['total_predictions'],
                    mode='lines+markers',
                    name='Total Predictions',
                    line=dict(color='blue')
                ),
                row=1, col=1
            )
            
            fig.add_trace(
                go.Scatter(
                    x=df_hourly['timestamp'],
                    y=df_hourly['fraud_count'],
                    mode='lines+markers',
                    name='Fraud Detections',
                    line=dict(color='red')
                ),
                row=1, col=1
            )
            
            # Average fraud probability
            fig.add_trace(
                go.Scatter(
                    x=df_hourly['timestamp'],
                    y=df_hourly['avg_fraud_prob'],
                    mode='lines+markers',
                    name='Avg Fraud Probability',
                    line=dict(color='orange')
                ),
                row=2, col=1
            )
            
            fig.update_layout(height=600, showlegend=True)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for time series analysis")
    
    with tab2:
        if not df.empty:
            # Risk level distribution
            col1, col2 = st.columns(2)
            
            with col1:
                fraud_dist = df['is_fraud'].value_counts()
                fig = px.pie(
                    values=fraud_dist.values,
                    names=['Normal', 'Fraud'],
                    title="Fraud Detection Distribution",
                    color_discrete_map={'Normal': 'lightgreen', 'Fraud': 'lightcoral'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Fraud probability histogram
                fig = px.histogram(
                    df,
                    x='fraud_probability',
                    nbins=20,
                    title="Fraud Probability Distribution",
                    color='is_fraud',
                    color_discrete_map={True: 'lightcoral', False: 'lightgreen'}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for risk analysis")
    
    with tab3:
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Amount distribution by fraud status
                fig = px.box(
                    df,
                    x='is_fraud',
                    y='amount',
                    title="Transaction Amount by Fraud Status",
                    color='is_fraud',
                    color_discrete_map={True: 'lightcoral', False: 'lightgreen'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Merchant category analysis
                merchant_stats = df.groupby(['merchant_category', 'is_fraud']).size().unstack(fill_value=0)
                if not merchant_stats.empty:
                    fig = px.bar(
                        merchant_stats,
                        title="Fraud by Merchant Category",
                        color_discrete_map={True: 'lightcoral', False: 'lightgreen'}
                    )
                    st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for amount analysis")
    
    with tab4:
        if not df.empty:
            col1, col2 = st.columns(2)
            
            with col1:
                # Processing time distribution
                fig = px.histogram(
                    df,
                    x='processing_time_ms',
                    nbins=20,
                    title="Processing Time Distribution",
                    color='is_fraud',
                    color_discrete_map={True: 'lightcoral', False: 'lightgreen'}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                # Processing time over time
                df_time_sorted = df.sort_values('timestamp')
                fig = px.scatter(
                    df_time_sorted,
                    x='timestamp',
                    y='processing_time_ms',
                    title="Processing Time Over Time",
                    color='is_fraud',
                    color_discrete_map={True: 'red', False: 'green'}
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for performance analysis")
    
    # Recent Predictions Table
    st.header("📝 Recent Predictions")
    
    if not df.empty:
        # Show last 10 predictions
        recent_df = df.nlargest(10, 'timestamp')[
            ['timestamp', 'amount', 'merchant_category', 'fraud_probability', 'is_fraud', 'processing_time_ms']
        ]
        
        # Style the dataframe
        def highlight_fraud(val):
            return 'background-color: #ffcdd2' if val else 'background-color: #c8e6c8'
        
        styled_df = recent_df.style.applymap(highlight_fraud, subset=['is_fraud'])
        st.dataframe(styled_df, use_container_width=True)
        
        # Export button
        if st.button("📥 Export All Data as CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"fraud_predictions_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    else:
        st.info("No recent predictions to display")
    
    # Auto-refresh logic
    if auto_refresh:
        time.sleep(30)
        st.rerun()

if __name__ == "__main__":
    main()
