# Portfolio Management with ML
## Overview

This Python code provides a framework for managing and simulating the performance of a financial portfolio. It uses the `yfinance` library to fetch historical stock data and scikit-learn's `RandomForestRegressor` for predicting future asset prices. The core components include:

-   **`Controller` Class:** This object handles the user input and calls the desired actions by creating an instance of the model class.
-   **`Model` Class:** Manages a collection of assets, fetches historical data, trains machine learning models, and simulates portfolio performance.
-   **`Asset` Class:** Represents a financial asset (e.g., stock) with attributes like ticker symbol, sector, asset class, quantity, and purchase price.
-   **`View` Class:** Handles the plotting of the data.

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

  Or see requirements.txt

## Installation

1.  Install the required packages:

    ```bash
    pip install -r requirements.txt
    ```

## Usage

- **Run the application:**
    ```bash
    python controller.py
    ```

    
## Limitations
1.  If you wish to speed up the process of training models, change the following line in model.py (238)
    ```python
    data = self.GetHistoricalData(asset.name , '50y') # Change to, for example, 5y.
    ```
    This may decrease the model's accuracy, but significantly speed up the training process.
    Moreover - a model is trained per asset. Less assets means faster training.
3.  If you wish to speed up the simulation process, the only thing you can do is to limit
   - The number of simulations
   - The prediction window. Both come with a price, of course
