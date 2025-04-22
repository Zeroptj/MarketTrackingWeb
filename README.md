# MarketTrackingWeb

MarketTrackingWeb is a Streamlit-based web application that helps users track and visualize financial market data across various asset classes. The application provides performance tracking for world indices, equities, fixed income, commodities, and cryptocurrencies, with customizable tracking features.

## Features

- **Multi-Asset Class Tracking**: Monitor performance across diverse asset classes
- **Interactive Data Visualization**: View performance changes across different time periods
- **Customizable Tracking**: Add your own ticker symbols to track specific assets
- **Comparative Analysis**: Heatmap visualization showing relative performance
- **Real-time Data**: Uses Yahoo Finance API to provide up-to-date market information

## Installation

### Prerequisites

- Python 3.7 or higher

### Setup Instructions

1. Download the ZIP file and extract it to your preferred location

2. Create a virtual environment and activate it:
   ```bash
   # On Windows
   python -m venv .venv
   .venv\Scripts\activate

   # On macOS/Linux
   python -m venv .venv
   source .venv/bin/activate
   ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   
   Note: If a requirements.txt file doesn't exist, create one with the following content:
   ```
   streamlit
   pandas
   numpy
   yfinance
   matplotlib
   plotly
   ```

## Running the Application

After installation, you can run the application using the following command:

```bash
streamlit run app.py
```

The application will start and open in your default web browser at `http://localhost:8501`.

## Project Structure

```
MarketTrackingWeb/
├── .venv/                  # Virtual environment directory (generated)
├── .streamlit/             # Streamlit configuration
│   └── config.toml         # Streamlit theme and server settings
├── app.py                  # Main application file
├── calculations.py         # Functions for data processing and calculations
├── data/                   # Data directory
│   └── Ticker.json         # JSON file containing ticker information
├── templates/              # HTML templates
│   └── table_template.html # HTML template for table visualization
├── .gitignore              # Git ignore file
└── README.md               # Project documentation
```

### Key Components

- **app.py**: The main application file containing the Streamlit UI code and application logic
- **calculations.py**: Contains utility functions for data retrieval and calculations
- **Ticker.json**: A configuration file that defines the asset categories and their corresponding ticker symbols
- **table_template.html**: HTML template with CSS styling for the data visualization tables

## Usage

1. Launch the application using the command mentioned in the "Running the Application" section
2. Use the sidebar to select the asset class you want to track (World Index, Equities, Fixed Income, etc.)
3. For Equities, you can further select between Region and Sector views
4. In the "My Tracking" section, you can add your own ticker symbols from Yahoo Finance to track specific assets

## Data Sources

The application uses the yfinance library to fetch financial data from Yahoo Finance.

## Customization

You can customize the tracked assets by modifying the `data/Ticker.json` file. The file organizes assets by categories and subcategories, making it easy to add or remove assets as needed.

