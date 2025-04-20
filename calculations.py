import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import plotly.graph_objects as go
import streamlit as st
import json

def read_tickers_from_file(file_path):
    with open(file_path, 'r') as file:
        categories = json.load(file)
    return categories

def get_stock_data(tickers):
    data = []
    for ticker in tickers:
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period="1y")  # Retrieve data for the past 1 year

            if hist.empty:  # Check if data exists
                raise ValueError(f"No data found for {ticker}")

            last_close = hist['Close'].iloc[-1]
            week_ago_close = hist['Close'].iloc[-6] if len(hist) > 5 else last_close
            month_ago_close = hist['Close'].iloc[-22] if len(hist) > 21 else last_close
            three_month_ago_close = hist['Close'].iloc[-66] if len(hist) > 65 else last_close
            six_month_ago_close = hist['Close'].iloc[-132] if len(hist) > 131 else last_close
            ytd_close = hist['Close'].iloc[0] if len(hist) > 0 else last_close

            data.append({
                "Ticker": ticker,
                "Name": stock.info.get('longName', 'N/A'),
                "Last Close": last_close,
                "1 Week Change (%)": ((last_close - week_ago_close) / week_ago_close) * 100,
                "1 Month Change (%)": ((last_close - month_ago_close) / month_ago_close) * 100,
                "3 Month Change (%)": ((last_close - three_month_ago_close) / three_month_ago_close) * 100,
                "6 Month Change (%)": ((last_close - six_month_ago_close) / six_month_ago_close) * 100,
                "YTD Change (%)": ((last_close - ytd_close) / ytd_close) * 100
            })
        
        except Exception as e:  # If data retrieval fails
            print(f"Warning: {ticker} - {e}")  # Display warning message
            data.append({
                "Ticker": ticker,
                "Name": "N/A",
                "Last Close": 0.0,  # Set a constant value, e.g., 100
                "1 Week Change (%)": 0.0,
                "1 Month Change (%)": 0.0,
                "3 Month Change (%)": 0.0,
                "6 Month Change (%)": 0.0,
                "YTD Change (%)": 0.0
            })
    
    return data

def calculate_sector_data(categories):
    """Create a Sector table categorized by type"""
    sector_data = []
    
    # Retrieve data for each Sector
    for sector, tickers in categories['Equity']['Sector'].items():
        stock_data = get_stock_data(tickers)
        for data in stock_data:
            sector_data.append({
                'Asset': sector,
                'Type': sector,  # Use Sector name as Type
                '1 Week Change (%)': data['1 Week Change (%)'],
                '1 Month Change (%)': data['1 Month Change (%)'],
                '3 Month Change (%)': data['3 Month Change (%)'],
                '6 Month Change (%)': data['6 Month Change (%)'],
                'YTD Change (%)':data['YTD Change (%)']
            })

    if not sector_data:
        return None

    df = pd.DataFrame(sector_data)
    
    # Rearrange columns
    columns = ['Asset', 'Type', '1 Week Change (%)', '1 Month Change (%)', 
              '3 Month Change (%)', '6 Month Change (%)','YTD Change (%)']
    df = df[columns]
    
    return df

def get_avg_changes(ticker):
    acwi = yf.Ticker(ticker)
    hist = acwi.history(period="10y")
    
    # Average changes
    changes = {
        '1 Week Change (%)': hist['Close'].pct_change(5).mean() * 100,  # 1 week
        '1 Month Change (%)': hist['Close'].pct_change(21).mean() * 100,  # 1 month
        '3 Month Change (%)': hist['Close'].pct_change(63).mean() * 100,  # 3 months
        '6 Month Change (%)': hist['Close'].pct_change(126).mean() * 100,  # 6 months
        'YTD Change (%)': hist['Close'].pct_change(252).mean() * 100  # YTD
    }
    return changes