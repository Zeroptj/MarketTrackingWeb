import streamlit as st
import pandas as pd
import calculations as cal
import os
import numpy as np
import io
import matplotlib.pyplot as plt

#base directory
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
#Path
categories = cal.read_tickers_from_file(os.path.join(BASE_DIR, 'data', 'Ticker.json'))
# HTML template
with open(os.path.join(BASE_DIR, 'templates', 'table_template.html'), 'r', encoding='utf-8') as f:
    html_template = f.read()

# web app
st.set_page_config(page_title="Market Tracking Web App", layout="wide", initial_sidebar_state="expanded")
st.title("Market Tracking Web App")

#side bar selectbox
option = st.sidebar.selectbox(
    'Select Index',
    ('World Index','Equities','Fixed Income','Commodity','Cryptocurrency','My Tracking')
)

#'World Index'
if option == 'World Index':
    st.header('World Index')
    indices=categories["indices"]
    #get_stock_data form calculations
    stock_data = cal.get_stock_data([item['ticker'] for item in indices.values()])
    
    # Process data
    data = []
    for item in stock_data:
        ticker = item['Ticker']
        name = next(k for k, v in indices.items() if v['ticker'] == ticker)
        asset_info = indices[name]
        
        data.append({
            'Asset': name,
            'Type': asset_info['type'],
            'Order': asset_info['order'],
            '1 Week Change (%)': item['1 Week Change (%)'],
            '1 Month Change (%)': item['1 Month Change (%)'],
            '3 Month Change (%)': item['3 Month Change (%)'],
            '6 Month Change (%)': item['6 Month Change (%)'],
            'YTD Change (%)': item['YTD Change (%)']
        })
    
    #Create DataFrame from data
    df_world = pd.DataFrame(data)
    df_world = df_world.sort_values(['Order'])
    
    # Set the order of the columns
    columns_to_display = [
        'Asset',
        '1 Week Change (%)',
        '1 Month Change (%)',
        '3 Month Change (%)',
        '6 Month Change (%)',
        'YTD Change (%)'
    ]
    
    # Type to adjusted color
    df_world = df_world[columns_to_display + ['Type']]

    numeric_cols = df_world.select_dtypes(include=[np.number]).columns
    df_world[numeric_cols] = df_world[numeric_cols].round(2)
    
    df_display = df_world.drop('Type', axis=1).set_index('Asset')
    type_series = df_world.set_index('Asset')['Type']
    
    # Calculate ACWI average changes
    acwi_rolling_changes = cal.get_avg_changes('ACWI')
    
    table_body = ""
    for name, row in df_display.iterrows():
        asset_type = type_series[name].lower().replace(' ', '-')
        is_acwi = 'acwi-row' if name == 'ACWI' else ''
        table_body += f'<tr class="{asset_type} {is_acwi}">'
        table_body += f'<td>{name}</td>'
        
        for col in numeric_cols:
            value = row[col]
            acwi_std = acwi_rolling_changes[col]
            # calculate heatmap class 
            if not pd.isna(value) and not pd.isna(acwi_std) and acwi_std != 0:
                diff = value - acwi_std
                abs_std = abs(value / acwi_std)
                if diff < 0:
                    if abs_std < 0.5:
                        heat_class = 'heat-0'
                    elif abs_std < 1:
                        heat_class = 'heat-1'
                    elif abs_std < 1.5:
                        heat_class = 'heat-2'
                    elif abs_std < 2:
                        heat_class = 'heat-3'
                    else:
                        heat_class = 'heat-4'
                if diff > 0:
                    if abs_std < 0.5:
                        heat_class = 'heat-p0'
                    elif abs_std < 1:
                        heat_class = 'heat-p1'
                    elif abs_std < 1.5:
                        heat_class = 'heat-p2'
                    elif abs_std < 2:
                        heat_class = 'heat-p3'
                    else:
                        heat_class = 'heat-p4'
            else:
                heat_class = ''
            formatted_value = f"{value:+.2f}%" if not pd.isna(value) else ''
            table_body += f'<td class="number-cell {heat_class}">{formatted_value}</td>'
        table_body += '</tr>'
    
    #{table_body} to template with real data
    html = html_template.replace('{table_body}', table_body)
    # HTML table
    st.write(html, unsafe_allow_html=True)

    # Heatmap Explanation
    st.write("### Heatmap Explanation")
    st.write("The heatmap values represent changes compared to the average changes of ACWI (MSCI All Country World Index).")
    st.write("The average changes of ACWI used as the baseline for comparison are:")
    for col in numeric_cols:
        st.write(f"**{col}:**Average %Chg = {acwi_rolling_changes[col]:+.2f}%")

# Equities
elif option == 'Equities':
    equity_option = st.sidebar.selectbox(
        'Select Equities Type',
        ('Region', 'Sector')
    )
    if equity_option == 'Region':
        st.header("Region")
        region_data = []
        
        # ดึงข้อมูลแต่ละภูมิภาค
        region_order = {
            'Americas': 1,  # กำหนดลำดับการแสดงผล
            'Europe': 2,
            'Asia': 3
        }
        
        for region, tickers in categories['Equity']['Region'].items():
            stock_data = cal.get_stock_data(tickers)
            for data in stock_data:
                name = {
                    'SPY': 'US',
                    'VGK': 'Europe',
                    'EWU': 'UK',
                    'AIA': 'Asia Pacific',
                    'EWJ': 'Japan',
                    'INDA': 'India',
                    'MCHI': 'China'
                }.get(data['Ticker'], data['Ticker'])
                
                region_data.append({
                    'Asset': name,
                    'Type': region,
                    'Order': region_order[region],  # เพิ่ม Order สำหรับการเรียงลำดับ
                    '1 Week Change (%)': data['1 Week Change (%)'],
                    '1 Month Change (%)': data['1 Month Change (%)'],
                    '3 Month Change (%)': data['3 Month Change (%)'],
                    '6 Month Change (%)': data['6 Month Change (%)'],
                    'YTD Change (%)': data['YTD Change (%)']
                })

        if not region_data:
            st.write("No data available for the selected region.")

        df_region = pd.DataFrame(region_data)
        # จัดเรียงตามภูมิภาคและชื่อสินทรัพย์
        df_region = df_region.sort_values(['Order', 'Asset'])
        
        # จัดเรียงคอลัมน์
        columns = ['Asset', 'Type', '1 Week Change (%)', '1 Month Change (%)', 
                '3 Month Change (%)', '6 Month Change (%)','YTD Change (%)']
        df_region = df_region[columns]
        numeric_cols = df_region.select_dtypes(include=[np.number]).columns
        df_region[numeric_cols] = df_region[numeric_cols].round(2)
        
        df_display = df_region.drop('Type', axis=1).set_index('Asset')
        type_series = df_region.set_index('Asset')['Type']

                # Calculate ACWI average changes
        acwi_rolling_changes = cal.get_avg_changes('ACWI')
        
        table_body = ""
        for name, row in df_display.iterrows():
            asset_type = type_series[name].lower().replace(' ', '-')
            is_acwi = 'acwi-row' if name == 'ACWI' else ''
            table_body += f'<tr class="{asset_type} {is_acwi}">'
            table_body += f'<td>{name}</td>'
            
            for col in numeric_cols:
                value = row[col]
                acwi_std = acwi_rolling_changes[col]
                # calculate heatmap class 
                if not pd.isna(value) and not pd.isna(acwi_std) and acwi_std != 0:
                    diff = value - acwi_std
                    abs_std = abs(value / acwi_std)
                    if diff < 0:
                        if abs_std < 0.5:
                            heat_class = 'heat-0'
                        elif abs_std < 1:
                            heat_class = 'heat-1'
                        elif abs_std < 1.5:
                            heat_class = 'heat-2'
                        elif abs_std < 2:
                            heat_class = 'heat-3'
                        else:
                            heat_class = 'heat-4'
                    if diff > 0:
                        if abs_std < 0.5:
                            heat_class = 'heat-p0'
                        elif abs_std < 1:
                            heat_class = 'heat-p1'
                        elif abs_std < 1.5:
                            heat_class = 'heat-p2'
                        elif abs_std < 2:
                            heat_class = 'heat-p3'
                        else:
                            heat_class = 'heat-p4'
                else:
                    heat_class = ''
                formatted_value = f"{value:+.2f}%" if not pd.isna(value) else ''
                table_body += f'<td class="number-cell {heat_class}">{formatted_value}</td>'
            table_body += '</tr>'
        
        #{table_body} to template with real data
        html = html_template.replace('{table_body}', table_body)
        # HTML table
        st.write(html, unsafe_allow_html=True)
        # Heatmap Explanation
        st.write("### Heatmap Explanation")
        st.write("The heatmap values represent changes compared to the average changes of ACWI (MSCI All Country World Index).")
        st.write("The average changes of ACWI used as the baseline for comparison are:")
        for col in numeric_cols:
            st.write(f"**{col}:**Average %Chg = {acwi_rolling_changes[col]:+.2f}%")

    elif equity_option == 'Sector':
        st.header("Sector")
        df_sector = cal.calculate_sector_data(categories)
        
        if df_sector is not None:
            numeric_cols = df_sector.select_dtypes(include=[np.number]).columns
            df_sector[numeric_cols] = df_sector[numeric_cols].round(2)
            
            # table body
            table_body = ""
            acwi_rolling_changes = cal.get_avg_changes('ACWI')
            
            #Sector Type
            sector_groups = {
                'Cyclical': ['Basic Materials','Consumer Cyclical', 'Financial Services', 'Real Estate'],
                'Sensitive': ['Communication Services','Energy',  'Industrials','Technology'],
                'Defensive': ['Consumer Defensive', 'Healthcare', 'Utilities']
            }
            
            # Sector
            for group_name, sectors in sector_groups.items():
                for sector in sectors:
                    sector_data = df_sector[df_sector['Type'] == sector]
                    
                    for _, row in sector_data.iterrows():
                        table_body += f'<tr class="{group_name.lower()}">'
                        table_body += f'<td>{row["Asset"]}</td>'
                        
                        for col in numeric_cols:
                            value = row[col]
                            acwi_std = abs(acwi_rolling_changes[col])
                            
                            # heatmap class
                            if not pd.isna(value) and not pd.isna(acwi_std) and acwi_std != 0:
                                diff = value - acwi_std
                                abs_std = abs(value / acwi_std)
                                if diff < 0:
                                    if abs_std < 0.5:
                                        heat_class = 'heat-0'
                                    elif abs_std < 1:
                                        heat_class = 'heat-1'
                                    elif abs_std < 1.5:
                                        heat_class = 'heat-2'
                                    elif abs_std < 2:
                                        heat_class = 'heat-3'
                                    else:
                                        heat_class = 'heat-4'
                                if diff > 0:
                                    if abs_std < 0.5:
                                        heat_class = 'heat-p0'
                                    elif abs_std < 1:
                                        heat_class = 'heat-p1'
                                    elif abs_std < 1.5:
                                        heat_class = 'heat-p2'
                                    elif abs_std < 2:
                                        heat_class = 'heat-p3'
                                    else:
                                        heat_class = 'heat-p4'
                            else:
                                heat_class = ''
                            
                            formatted_value = f"{value:+.2f}%" if not pd.isna(value) else ''
                            table_body += f'<td class="number-cell {heat_class}">{formatted_value}</td>'
                        
                        table_body += '</tr>'
            

            html = html_template.replace('{table_body}', table_body)
            st.write(html, unsafe_allow_html=True)
        # Heatmap Explanation
        st.write("### Heatmap Explanation")
        st.write("The heatmap values represent changes compared to the average changes of ACWI (MSCI All Country World Index).")
        st.write("The average changes of ACWI used as the baseline for comparison are:")
        for col in numeric_cols:
            st.write(f"**{col}:**Average %Chg = {acwi_rolling_changes[col]:+.2f}%")


elif option == 'Fixed Income':
    st.header("Fixed Income")
    
    # Combine all data
    all_data = []
    for category, tickers in categories['Fixed Income'].items():
        stock_data = cal.get_stock_data(tickers)
        for data in stock_data:
            data['Category'] = category  # Add category information
            all_data.append(data)
    
    if all_data:
        df = pd.DataFrame(all_data)
        
        # Format numeric columns to 2 decimal places
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].round(2)
        
        # Replace names with more descriptive labels
        df = df.replace({
            'iShares 1-3 Year Treasury Bond ETF': 'Short-Term Fixed Income',
            'iShares 3-7 Year Treasury Bond ETF': 'Medium-Term Fixed Income',
            'iShares 20+ Year Treasury Bond ETF': 'Long-Term Fixed Income',
            'iShares iBoxx $ Investment Grade Corporate Bond ETF': 'Investment Grade Fixed Income',
            'iShares iBoxx $ High Yield Corporate Bond ETF': 'High Yield Fixed Income',
        })
        
        # Create table body grouped by category
        table_body = ""
        fix_avg_changes = cal.get_avg_changes('IEI')
        for category in ['Government Bonds', 'Corporate Bonds']:
            category_data = df[df['Category'] == category]
            
            for _, row in category_data.iterrows():
                table_body += f'<tr class="{category.lower().replace(" ", "-")}">'
                table_body += f'<td>{row["Name"]}</td>'
                
                for col in ['1 Week Change (%)', '1 Month Change (%)', '3 Month Change (%)', 
                           '6 Month Change (%)', 'YTD Change (%)']:
                    value = row[col]
                    agg_std = abs(fix_avg_changes[col])
                    # คำนวณ heatmap class
                    if not pd.isna(value) and not pd.isna(agg_std) and agg_std != 0:
                        diff = value - agg_std
                        abs_std = abs(value / agg_std)
                        if diff < 0:
                            if abs_std < 0.5:
                                heat_class = 'heat-0'
                            elif abs_std < 1:
                                heat_class = 'heat-1'
                            elif abs_std < 1.5:
                                heat_class = 'heat-2'
                            elif abs_std < 2:
                                heat_class = 'heat-3'
                            else:
                                heat_class = 'heat-4'
                        if diff > 0:
                            if abs_std < 0.5:
                                heat_class = 'heat-p0'
                            elif abs_std < 1:
                                heat_class = 'heat-p1'
                            elif abs_std < 1.5:
                                heat_class = 'heat-p2'
                            elif abs_std < 2:
                                heat_class = 'heat-p3'
                            else:
                                heat_class = 'heat-p4'
                    else:
                        heat_class = ''
                    formatted_value = f"{value:+.2f}%" if not pd.isna(value) else ''
                    table_body += f'<td class="number-cell {heat_class}">{formatted_value}</td>'
                
                table_body += "</tr>"
        # Replace {table_body} in the template with actual data
        html = html_template.replace('{table_body}', table_body)
        # Display the HTML table
        st.write(html, unsafe_allow_html=True)
    # Heatmap Explanation
    st.write("### Heatmap Explanation")
    st.write("The average changes of the selected fixed income category are:")
    for col in numeric_cols:
        if col in fix_avg_changes:
            st.write(f"**{col}:** Average %Chg = {fix_avg_changes[col]:+.2f}%")

elif option == 'Commodity':
    st.header("Commodity")
    
    # Combine all data
    all_data = []
    for category, tickers in categories['Commodity'].items():
        stock_data = cal.get_stock_data(tickers)
        for data in stock_data:
            data['Category'] = category  # Add category information
            all_data.append(data)
    
    if all_data:
        df = pd.DataFrame(all_data)
        
        # Format numeric columns to 2 decimal places
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].round(2)
        df = df.replace({
            'SPDR Gold MiniShares': 'Gold',
            'iShares Silver Trust': 'Silver',
            'United States Oil Fund, LP': 'Oil',
            'United States Natural Gas Fund, LP': 'Natural Gas',
            'Invesco DB Agriculture Fund': 'Agriculture',
        })
        
        # Create table body grouped by category
        table_body = ""
        com_avg_changes = cal.get_avg_changes('GLDM')
        for category in ['Precious Metals', 'Energy', 'Agriculture']:
            category_data = df[df['Category'] == category]
            
            for _, row in category_data.iterrows():
                table_body += f'<tr class="{category.lower().replace(" ", "-")}">'
                table_body += f'<td>{row["Name"]}</td>'
                
                for col in ['1 Week Change (%)', '1 Month Change (%)', '3 Month Change (%)', 
                           '6 Month Change (%)', 'YTD Change (%)']:
                    value = row[col]
                    agg_std = abs(com_avg_changes[col])
                    # คำนวณ heatmap class
                    if not pd.isna(value) and not pd.isna(agg_std) and agg_std != 0:
                        diff = value - agg_std
                        abs_std = abs(value / agg_std)
                        if diff < 0:
                            if abs_std < 0.5:
                                heat_class = 'heat-0'
                            elif abs_std < 1:
                                heat_class = 'heat-1'
                            elif abs_std < 1.5:
                                heat_class = 'heat-2'
                            elif abs_std < 2:
                                heat_class = 'heat-3'
                            else:
                                heat_class = 'heat-4'
                        if diff > 0:
                            if abs_std < 0.5:
                                heat_class = 'heat-p0'
                            elif abs_std < 1:
                                heat_class = 'heat-p1'
                            elif abs_std < 1.5:
                                heat_class = 'heat-p2'
                            elif abs_std < 2:
                                heat_class = 'heat-p3'
                            else:
                                heat_class = 'heat-p4'
                    else:
                        heat_class = ''
                    formatted_value = f"{value:+.2f}%" if not pd.isna(value) else ''
                    table_body += f'<td class="number-cell {heat_class}">{formatted_value}</td>'
                table_body += "</tr>"
        
        # Replace {table_body} in the template with actual data
        html = html_template.replace('{table_body}', table_body)
        
        # Display the HTML table
        st.write(html, unsafe_allow_html=True)
    # Heatmap Explanation
    st.write("### Heatmap Explanation")
    st.write("The average changes of the selected Commodity category are:")
    for col in numeric_cols:
        if col in com_avg_changes:
            st.write(f"**{col}:** Average %Chg = {com_avg_changes[col]:+.2f}%")

elif option == 'Cryptocurrency':
    st.header("Cryptocurrency")
    # Combine all data
    all_data = []
    for category, tickers in categories['Cryptocurrency'].items():
        stock_data = cal.get_stock_data(tickers)
        for data in stock_data:
            data['Category'] = category  # Add category information
            all_data.append(data)
    
    if all_data:
        df = pd.DataFrame(all_data)
        
        # Format numeric columns to 2 decimal places
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        df[numeric_cols] = df[numeric_cols].round(2)
        df['Name'] = df['Name'].str.replace(' USD', '', regex=False)
        
        table_body = ""
        btc_avg_changes = cal.get_avg_changes('BTC-USD')
        for category in ['Bitcoin', 'Layer-1']:
            category_data = df[df['Category'] == category]
            
            for _, row in category_data.iterrows():
                table_body += f'<tr class="{category.lower().replace(" ", "-")}">'
                table_body += f'<td>{row["Name"]}</td>'
                
                for col in ['1 Week Change (%)', '1 Month Change (%)', '3 Month Change (%)', 
                           '6 Month Change (%)', 'YTD Change (%)']:
                    value = row[col]
                    btc_std = abs(btc_avg_changes[col])
                    if not pd.isna(value) and not pd.isna(btc_std) and btc_std != 0:
                        diff = value - btc_std
                        abs_std = abs(value / btc_std)
                        if diff < 0:
                            if abs_std < 0.5:
                                heat_class = 'heat-0'
                            elif abs_std < 1:
                                heat_class = 'heat-1'
                            elif abs_std < 1.5:
                                heat_class = 'heat-2'
                            elif abs_std < 2:
                                heat_class = 'heat-3'
                            else:
                                heat_class = 'heat-4'
                        if diff > 0:
                            if abs_std < 0.5:
                                heat_class = 'heat-p0'
                            elif abs_std < 1:
                                heat_class = 'heat-p1'
                            elif abs_std < 1.5:
                                heat_class = 'heat-p2'
                            elif abs_std < 2:
                                heat_class = 'heat-p3'
                            else:
                                heat_class = 'heat-p4'
                    else:
                        heat_class = ''
                    formatted_value = f"{value:+.2f}%" if not pd.isna(value) else ''
                    table_body += f'<td class="number-cell {heat_class}">{formatted_value}</td>'
        
        # Replace {table_body} in the template with actual data
        html = html_template.replace('{table_body}', table_body)
        
        # Display the HTML table
        st.write(html, unsafe_allow_html=True)
        # Heatmap Explanation
    st.write("### Heatmap Explanation")
    st.write("The average changes of the selected Cryptocurrency category are:")
    for col in numeric_cols:
        if col in btc_avg_changes:
            st.write(f"**{col}:** Average %Chg = {btc_avg_changes[col]:+.2f}%")

elif option == 'My Tracking':
    st.header("My Tracking")
    
    # Initialize session state for storing tickers if not exists
    if 'tickers' not in st.session_state:
        st.session_state.tickers = []
    
    # Initialize dictionary for final data collection if not exists
    if 'final_data' not in st.session_state:
        st.session_state.final_data = {}
    
    # Initialize counter for dynamic fields if not exists
    if 'ticker_count' not in st.session_state:
        st.session_state.ticker_count = 1
    
    # Function to add more ticker fields
    def add_ticker_field():
        st.session_state.ticker_count += 1
    
    # Function to remove ticker field
    def remove_ticker_field():
        if st.session_state.ticker_count > 1:
            st.session_state.ticker_count -= 1
    
    # Function to reset ticker fields
    def reset_ticker_fields():
        st.session_state.ticker_count = 1
    
    # Function to organize tickers by asset class
    def organize_tickers_by_asset_class():
        organized_data = {}
        for item in st.session_state.tickers:
            asset_class = item["asset_class"]
            ticker = item["ticker"]
            
            if asset_class not in organized_data:
                organized_data[asset_class] = []
            
            organized_data[asset_class].append(ticker)
        
        return organized_data

    # Asset class options
    asset_classes = ['Equity', 'Fixed Income', 'Commodity', "Other"]
    
    # Add buttons to manage ticker fields
    col1, col2, = st.columns([5, 1])
    with col1:
        st.button("+ Add Field", on_click=add_ticker_field)
    with col2:
        st.button("- Remove Field", on_click=remove_ticker_field, disabled=st.session_state.ticker_count <= 1)
    # Form for adding new tickers
    with st.form(key="add_ticker_form"):
        # Create dynamic number of ticker input fields
        ticker_inputs = []
        asset_class_inputs = []
        
        for i in range(st.session_state.ticker_count):
            col1, col2 = st.columns([2, 1])
            with col1:
                ticker_input = st.text_input(f"Ticker Symbol #{i+1}", key=f"ticker_input_{i}")
                ticker_inputs.append(ticker_input)
            with col2:
                asset_class_input = st.selectbox(f"Asset Class #{i+1}", asset_classes, key=f"asset_class_input_{i}")
                asset_class_inputs.append(asset_class_input)
        
        submit_col, reset_col = st.columns([5, 1])
        with submit_col:
            submit_button = st.form_submit_button(label="Add Tickers")
        with reset_col:
            reset_button = st.form_submit_button(label="Reset Fields", on_click=reset_ticker_fields)
        
        if submit_button:
            # Add new tickers to session state
            added_count = 0
            for i in range(len(ticker_inputs)):
                if ticker_inputs[i]:  # Only add if ticker is not empty
                    st.session_state.tickers.append({
                        "ticker": ticker_inputs[i],
                        "asset_class": asset_class_inputs[i]
                    })
                    added_count += 1
            
            if added_count > 0:
                st.success(f"Added {added_count} ticker(s) successfully")
                # Reset field count after successful submission
                st.session_state.ticker_count = 1
    
    # Display current tickers if any
    if st.session_state.tickers:
        col1, col2 = st.columns([5, 1])
        with col1:
            # Add submit button to finalize data collection
            if st.button("Submit All Tickers"):
                # Organize tickers by asset class
                organized_data = organize_tickers_by_asset_class()
                
                # Store in session state for later use
                st.session_state.final_data = organized_data
                # Display the final dictionary
        with col2:    
            # Add button to clear all tickers
            if st.button("Clear All Tickers"):
                st.session_state.tickers = []
                st.success("All tickers cleared")

    # get_stock_data form calculations
    if 'final_data' in st.session_state and st.session_state.final_data:
        # Combine all tickers from all asset classes into a dictionary format
        all_tickers = {}
        for asset_class, tickers in st.session_state.final_data.items():
            for ticker in tickers:
                all_tickers[ticker] = {"asset_class": asset_class, "ticker": ticker}

        all_tickers_list = [item['ticker'] for item in all_tickers.values()]
        stock_data = []

        # ปรับส่วนการเรียกใช้ get_stock_data
        try:
            stock_data = cal.get_stock_data(all_tickers_list)
        except Exception as e:
            st.error(f"Error fetching stock data: {e}")

        # Process data
        data = []
        for item in stock_data:
            try:
                ticker = item['Ticker']
                ticker_match = None
                for name, info in all_tickers.items():
                    if info['ticker'] == ticker:
                        ticker_match = name
                        break

                if ticker_match:  
                    asset_info = all_tickers[ticker_match]
                    data.append({
                        'Asset': ticker_match,
                        'Type': asset_info['asset_class'],
                        '1 Week Change (%)': item.get('1 Week Change (%)', None),
                        '1 Month Change (%)': item.get('1 Month Change (%)', None),
                        '3 Month Change (%)': item.get('3 Month Change (%)', None),
                        '6 Month Change (%)': item.get('6 Month Change (%)', None),
                        'YTD Change (%)': item.get('YTD Change (%)', None)
                    })
            except Exception as e:
                st.warning(f"Skipping ticker '{item.get('Ticker', 'Unknown')}' due to error: {e}")
                continue

        # Create DataFrame from data
        df_world = pd.DataFrame(data)
        type_order = ['Equity', 'Fixed Income', 'Commodity', 'Other']
        df_world['Type'] = pd.Categorical(df_world['Type'], categories=type_order, ordered=True)
        df_world = df_world.sort_values(['Type'])
        
        # Set the order of the columns
        columns_to_display = [
            'Asset',
            '1 Week Change (%)',
            '1 Month Change (%)',
            '3 Month Change (%)',
            '6 Month Change (%)',
            'YTD Change (%)'
        ]
        
        # Type to adjusted color
        df_world = df_world[columns_to_display + ['Type']]
        numeric_cols = df_world.select_dtypes(include=[np.number]).columns
        df_world[numeric_cols] = df_world[numeric_cols].round(2)
        
        df_display = df_world.drop('Type', axis=1).set_index('Asset')
        type_series = df_world.set_index('Asset')['Type']
        
        # Calculate ACWI average changes
        acwi_rolling_changes = cal.get_avg_changes('ACWI')
        
        table_body = ""
        for name, row in df_display.iterrows():
            asset_type = type_series[name].lower().replace(' ', '-')
            is_acwi = 'acwi-row' if name == 'ACWI' else ''
            table_body += f'<tr class="{asset_type} {is_acwi}">'
            table_body += f'<td>{name}</td>'
            
            for col in numeric_cols:
                value = row[col]
                acwi_std = acwi_rolling_changes[col]
                # calculate heatmap class 
                if not pd.isna(value) and not pd.isna(acwi_std) and acwi_std != 0:
                    diff = value - acwi_std
                    abs_std = abs(value / acwi_std)
                    if diff < 0:
                        if abs_std < 0.5:
                            heat_class = 'heat-0'
                        elif abs_std < 1:
                            heat_class = 'heat-1'
                        elif abs_std < 1.5:
                            heat_class = 'heat-2'
                        elif abs_std < 2:
                            heat_class = 'heat-3'
                        else:
                            heat_class = 'heat-4'
                    if diff > 0:
                        if abs_std < 0.5:
                            heat_class = 'heat-p0'
                        elif abs_std < 1:
                            heat_class = 'heat-p1'
                        elif abs_std < 1.5:
                            heat_class = 'heat-p2'
                        elif abs_std < 2:
                            heat_class = 'heat-p3'
                        else:
                            heat_class = 'heat-p4'
                else:
                    heat_class = ''
                formatted_value = f"{value:+.2f}%" if not pd.isna(value) else ''
                table_body += f'<td class="number-cell {heat_class}">{formatted_value}</td>'
            table_body += '</tr>'
        
        #{table_body} to template with real data
        html = html_template.replace('{table_body}', table_body)
        # HTML table
        st.write(html, unsafe_allow_html=True)

        # Heatmap Explanation
        st.write("### Heatmap Explanation")
        st.write("The heatmap values represent changes compared to the average changes of ACWI (MSCI All Country World Index).")
        st.write("The average changes of ACWI used as the baseline for comparison are:")
        for col in numeric_cols:
            st.write(f"**{col}:**Average %Chg = {acwi_rolling_changes[col]:+.2f}%")

            




            
        
 
            

    