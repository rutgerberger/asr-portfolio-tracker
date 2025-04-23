import yfinance as yf
import pandas as pd
import numpy as np
import datetime

#ML libraries
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor


class Asset():
    def __init__(self, ticker: str, sector: str, asset_class: str, quantity: int, price: float):
        self.name = ticker
        self.ticker = yf.Ticker(ticker)
        self.sector = sector
        self.asset_class = asset_class
        self.quantity = quantity
        self.purchase_price = price
        self.value = 0 #Only used for prediction purposes

    def GetPrice(self):
        """
        Shorthand for if you wish to get the current price an
        known asset within your portfolio
        """
        return self.ticker.info['currentPrice']
    
    def SetValue(self, value):
        """
        When simulating, this function updates the estimated value of the
        asset
        """
        self.value = value

    def __str__(self):
        return self.name
    


class Model():
    def __init__(self):
        self.assets = set()

    def VerifyTicker(self, ticker: str):
        """
        Checks if the ticker is valid.
        If there is any recent data on the ticker,
        this returns true. None otherwise.
        """
        try:
            hist = yf.Ticker(ticker).history(
                period='1mo')
            if len(hist) > 0:
                return yf.Ticker(ticker)
            else:
                return None
        except:
            return None # If that failed, it will not exist either 

    def AddTicker(self, ticker: str, sector: str, asset_class: str, quantity: int, price: float):
        """
        Given a ticker name (assumed to be validated), sector, asset class, quantity and price
        This function adds the asset to the user's portfolio
        """
        NewAsset = Asset(ticker, sector, asset_class, quantity, price)
        #with open("portfolio.txt", 'w') as f:
        #    f.write("ticker")
        self.assets.add(NewAsset)
        return NewAsset

    def GetAssets(self):
        """
        Returns the set of assets in the portfolio
        """
        return self.assets
    
    def GetHistoricalData(self, ticker: str, length: str = '1y'):
        """
        Get historical data of the provided ticker (can be any)
        Returns None if the ticker does not exist
        Returns pd.dataframe otherwise
        """
        try:
            asset = yf.Ticker(ticker)
        except:
            return None
        historical_data = asset.history(period=length)
        return historical_data
    
    def GetPrice(self, ticker: str):
        """
        Get current price of the provided ticker (can be any)
        Returns none if the ticker does not exist
        Returns float otherwise
        """
        try:
            asset = yf.Ticker(ticker)
        except:
            return None
        return asset.info['currentPrice']
    
    def GetWeight(self, ticker: Asset, all_assets: set):
        """
        Calculates the relative weight of the given asset in the
        portfolio
        """
        total_value = 0
        asset_value = ticker.quantity * ticker.GetPrice()

        for asset in all_assets:
            total_value += asset.quantity * asset.GetPrice()

        return asset_value/total_value

    
    def GetCalculations(self, option, asset_class = None, sector = None):
        """
        Get the components of your portfolio.
        Dependent on option ('total/class/sector'), assets are selected.
        Returns a list of dictionaries, where each dictionary contains the
         - name
         - weight
         - value 
        of selected assets.
        """
        calculations = list()
        if option == 'total':
            for asset in self.assets:
                asset_dict = {"ticker": asset.name, "weight": round(self.GetWeight(asset, self.assets),3), "value": asset.quantity * asset.GetPrice()}
                calculations.append(asset_dict)
        elif option == 'class':
            all_assets = set()
            for asset in self.assets:
                if asset.asset_class == asset_class:
                    all_assets.add(asset)
            for asset in self.assets:
                if asset.asset_class == asset_class:
                    asset_dict = {"ticker": asset.name, "weight": round(self.GetWeight(asset, all_assets),3), "value": asset.quantity * asset.GetPrice()}
                    calculations.append(asset_dict)
        elif option == 'sector':
            all_assets = set()
            for asset in self.assets:
                if asset.sector == sector:
                    all_assets.add(asset)
                if asset.sector == sector:
                    asset_dict = {"ticker": asset.name, "weight": round(self.GetWeight(asset, all_assets),3), "value": asset.quantity * asset.GetPrice()}
                    calculations.append(asset_dict)
        return calculations
    
    def GetPortfolioValue(self, option='total', label = 'none'):
        """
        Returns the total portfolio value
        """
        total_value = 0
        for asset in self.assets:
            if option == 'class' and asset.asset_class == label:
                total_value += asset.quantity * asset.GetPrice()
            elif option == 'sector' and asset.sector == label:
                total_value += asset.quantity * asset.GetPrice()
            if option == 'total':
                total_value += asset.quantity * asset.GetPrice()
        return total_value

    def TransformData(self, data, look_back):
        """
        Creates rows with historical data included to train the 
        RF model on. Assumes that the closing price of the next 
        day is the one we want to predict and the closing of the
        previous is everything we know.
        """
        cols = []
        col_names = []

        # A for loop to create row wise data with history
        # to train the regressor on
        for day in range(look_back):
            item = data.iloc[day:].reset_index(drop=True).copy()
            cols.append(item)
            col_names.append(f"Close_{day}")

        merged = pd.concat(cols,ignore_index=True,axis=1)
        merged = merged[:-look_back]
        merged.columns = col_names
        for col in merged.columns:
            if "id_" in col:
                merged.drop(columns=col, inplace=True)

        return merged

    def SplitData(self, data):
        """
        Splits the provided data into y (we want to predict)
        and X (feature matrix). Useful for training.
        """
        y = data['Close_0'] # We want to predict the closing of the next day)
        X = data.drop(columns=['Close_0']) # We have every information except these points )
        return X, y

    def TrainModels(self, look_back=60):
        """
        Seperate function to train ML model.
        """
        initial_assets = [Asset('AAPL', 'Technology', 'Equity', 3, 29), Asset('MSFT', 'Technology', 'Equity', 3, 29)]
        # Train a simple RF model for each asset
        print("Training models.")
        models = {}

        for asset in initial_assets:
            model = RandomForestRegressor() # Input data is quite limited, random forest often sufficient
            data = self.GetHistoricalData(asset.name , '5y')['Close']
            data = self.TransformData(data, look_back)
            X, y = self.SplitData(data)
            
            if X is not None:
                X_train, _, y_train, _ = train_test_split(X, y, test_size=0.2, random_state=42)
                model.fit(X_train, y_train)
                models[asset.name] = model

            else:
                print(f"Could not prepare data for {asset.name}")

        return models

    #Create a ML model
    def SimulatePortfolio(self, num_simulations=10, forecast_years=15, look_back=30):

        num_timesteps = forecast_years * 252
        portfolio_futures = []
        assets = [Asset('AAPL', 'Technology', 'Equity', 3, 29), Asset('MSFT', 'Technology', 'Equity', 3, 29)]
        models = self.TrainModels(look_back)
        print("Calculating simulations...")
        
        start = datetime.datetime.now()

        col_names = [f"Close_{day}" for day in range(1, look_back)]

        for sim in range(num_simulations):
            print("Simulation:", sim)
            portfolio_values = [sum(asset.quantity * asset.value for asset in assets)]
            #^ Copy by value so they don't get overwritten
        
            asset_sequences = dict() # A dictionary which keeps track of all sequences per asset
            for asset in assets:
                data = self.GetHistoricalData(asset.name, '2y')['Close']
                last_sequence = self.TransformData(data, look_back)
                X, _ = self.SplitData(last_sequence)
                asset_sequences[asset.name] = X[0:1]
                asset_sequences[asset.name].columns = col_names

            ts_start = datetime.datetime.now()
            for t in range(num_timesteps):
                values = []
                for asset in assets:
                    if asset.name in models:
                        predicted_price = models[asset.name].predict(asset_sequences[asset.name]) # Predicted closing price for the next day by the model
                        random_shock = np.random.normal(0, 1)
                        predicted_price += random_shock

                        data = dict(P=predicted_price)
                        new_item = pd.DataFrame(data, index=[0])

                        values.append(asset.quantity * predicted_price) # Create new asset to add
                        sequence = pd.concat([new_item, asset_sequences[asset.name]], ignore_index=True, axis=1).iloc[:, :-1]
                        sequence.columns = col_names
                        asset_sequences[asset.name] = sequence

                current_portfolio_value = sum(values)
                portfolio_values.append(current_portfolio_value)
            print(f"Simulation {sim} time {datetime.datetime.now() - ts_start}")
            portfolio_futures.append(portfolio_values)

        t_time = datetime.datetime.now() - start
        print(f"Elapsed time: ", {t_time})

        return portfolio_futures

