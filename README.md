# OmegaFin

This open-source project is designed for gathering, processing, and analyzing financial data. Whether you're interested in real-time tick data, historical OHLC data, or using processed data to train machine learning models, OmegaFin offers the tools you need.

## Overview

OmegaFin is composed of several components that work together to manage and analyze financial data:

### Main App

The core of OmegaFin handles the following processes:

- **Live Data via FIX Protocol**:
  - **Data Collection**: Retrieves live tick data using the FIX protocol and stores it in Redis.
  - **Data Cleaning**: Cleans the live data and saves the cleaned version in another Redis instance.

- **Data Engineering**:
  - Processes both live and historical data, performs feature engineering, and stores the processed data in a PostgreSQL database with TimescaleDB for efficient time-series management.

- **Historical Data Handling**:
  - **Item Listing**: Generates a list of all available items, such as forex pairs.
  - **Pair Enabling**: Users can enable specific pairs, prompting the system to retrieve all historical OHLC (Open, High, Low, Close) data for all timeframes.
  - **Data Storage**: Historical data is saved to Redis, where it undergoes feature engineering.

- **Scheduler**: Runs every minute to update historical OHLC data, ensuring that the system always has up-to-date information.

- **Windows Agent Integration**:
  - **Socket Connection**: The main app can connect to a Windows Agent via socket. The agent serves as a bridge to MetaTrader 5 (MT5), sending data from MT5 to the server.
  - **Order Management**: The agent also accepts requests from the server to place orders, enabling seamless trading operations.
 
    
### Ctrader Open API Credentials

To access historical data, you need credentials from the Ctrader Open API. The process to obtain these credentials is free:

1. Visit the [Ctrader Open API](https://openapi.ctrader.com/).
2. Sign up for an account if you don't have one.
3. Create an application to obtain your **Client ID** and **Client Secret**.
4. set credentials as environment variables in .env.

