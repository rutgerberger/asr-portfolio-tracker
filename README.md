# Portfolio Management with Machine Learning

## Overview

This Python code provides a framework for managing and simulating the performance of a financial portfolio. It uses the `yfinance` library to fetch historical stock data and scikit-learn's `RandomForestRegressor` for predicting future asset prices. The core components include:

-   **`Asset` Class:** Represents a financial asset (e.g., stock) with attributes like ticker symbol, sector, asset class, quantity, and purchase price.
-   **`Model` Class:** Manages a collection of assets, fetches historical data, trains machine learning models, and simulates portfolio performance.

## Features

-   **Asset Management:**
    -   Creation of `Asset` objects with relevant properties.
    -   Adding and retrieving assets in a portfolio.
-   **Data Retrieval:**
    -   Fetching historical stock data from Yahoo Finance using `yfinance`.
    -   Verifying the validity of ticker symbols.
-   **Portfolio Analysis:**
    -   Calculating asset weights within the portfolio.
    -   Retrieving asset values and total portfolio value.
    -   Getting portfolio composition by asset class or sector.
-   **Price Prediction:**
    -   Preparing historical data for machine learning.
    -   Training a `RandomForestRegressor` model to predict daily price changes for each asset.
-   **Simulation:**
    -   Simulating portfolio performance over a specified period using predicted price changes.
    -   Accounting for price randomness using a normal distribution.
    -   Generating multiple simulations to analyze potential future portfolio values.

## Dependencies

-   Python 3.x
-   yfinance
-   pandas
-   numpy
-   scikit-learn
-   matplotlib

-   See requirements.txt

## Installation

1.  Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

- **Run the application:"**
    - Run: python controller.py
