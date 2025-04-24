import yfinance as yf
import pandas as pd
import numpy as np
import datetime

#ML libraries
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor


class Asset():
    """
    An Asset object is used within calculations and keeps track
    of the assigned features, such as the sector, class or 
    quantity.
    """
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
            for asset in self.assets:
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

    def GetAssetFeatures(self, data):
        """
        Returns dataframe with features we want to train RF
        model on - daily change - percentual change - log
        returns - closing price and volatility
        """
        df = pd.DataFrame()

        df['DailyChange'] = data['Close'] - data['Open']
        df['PctChange'] = data['Close'].pct_change()
        df['LogReturns'] = np.log(data['Close'] / data['Close'].shift(1))
        df['Close'] = data['Close']

        # Calculate Volatility (using a rolling standard deviation of log returns))
        window = 20
        df['Volatility'] = df['LogReturns'].rolling(window=window).std() * np.sqrt(252)
        return df.dropna() # No NaN values  

    def TransformData(self, data, look_back):
        """
        Creates rows with historical data included to train the 
        RF model on. Assumes that the closing price of the next 
        day is the one we want to predict and the closing of the
        previous days is everything we can know.
        """
        cols = []
        col_names = []

        # A for loop to create row wise data with history
        # to train the regressor on
        for day in range(look_back):
            item = data.iloc[day:].reset_index(drop=True).copy()
            cols.append(item)
            for column in data.columns:
                col_names.append(f"{column}_{day}")

        merged = pd.concat(cols,ignore_index=True,axis=1)
        merged = merged[:-look_back]
        merged.columns = col_names
        for col in merged.columns:
            if "id_" in col or "index_" in col:
                merged.drop(columns=col, inplace=True)

        return merged.dropna()

    def SplitData(self, data):
        """
        Splits the provided data into y (we want to predict)
        and X (feature matrix). Useful for training purposes
        """
        y = data['DailyChange_0'] # We want to predict the daily of the current day
        X = data.drop(columns=['DailyChange_0', 'PctChange_0', 'LogReturns_0', 'Close_0', 'Volatility_0']) # We have every information the current day
        return X, y

    def TrainModels(self, look_back=60):
        """
        Seperate function to train random forest
        models. Used within the simulation.
        Trains a seperate model for each
        asset within the portfolio
        """
        assets = self.assets
        print("Training models.")
        models = {}

        for asset in assets:
            model = RandomForestRegressor() # Input data is quite limited, random forest often sufficient
            data = self.GetHistoricalData(asset.name , '10y')
            print("Retrieved historical data...")
            data = self.GetAssetFeatures(data)
            print("Calculated features for historical data...")
            data = self.TransformData(data, look_back)
            X, y = self.SplitData(data)
            print("Preprocessed data... now training (this can take some time!)")
            
            if X is not None:
                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)
                model.fit(X_train, y_train)
                models[asset.name] = model
                #We could test accuracy by predicting test set:
                #y_pred = model.predict(X_test)
                #error = sklearn....MeanSquaredError(y_test, y_pred)
                #error = sklearn....MeanAbsoluteError(y_test, y_pred)

            else:
                print(f"Could not prepare data for {asset.name}")

        return models

    def SimulatePortfolio(self, num_simulations=10, forecast_years=15, look_back=30):
        """
        This function first trains a rf regressor based on historical price data
        It then simulates step by step behaviour of the index
        This way, a simulation takes +- 2 min -> therefore less than 
        100_000 simulations are suggested.
        """
        num_timesteps = forecast_years * 252 # Number of trading days each year
        portfolio_futures = []
        assets = self.assets
        models = self.TrainModels(look_back)
        print("Calculating simulations...")
        
        start = datetime.datetime.now()

        for sim in range(num_simulations):
            print("Simulation:", sim)
            portfolio_values = [sum(asset.quantity * asset.value for asset in assets)]
            #^ Copy by value so they don't get overwritten
        
            asset_sequences = dict() # A dictionary which keeps track of all sequences per asset
            calc_sequences = dict()
            for asset in assets:
                data = self.GetHistoricalData(asset.name, '2y')
                #We use calc_sequences to create the feature data with
                #Features such as the volatility requires a look-back window
                calc_sequences[asset.name] = data[['Open', 'Close']].reset_index()
                #And this is for the true prediction purposes
                data = self.GetAssetFeatures(calc_sequences[asset.name])
                asset_sequences[asset.name] = data.reset_index(drop=True)
            ts_start = datetime.datetime.now()
            for t in range(num_timesteps):
                values = []
                for asset in assets:
                    if asset.name in models:
                        last_sequence = asset_sequences[asset.name].iloc[-(look_back+1):].copy()
                        X = self.TransformData(pd.DataFrame(last_sequence), look_back)
                        X = X.iloc[[-1]] #get the last row
                        X, _ = self.SplitData(X)
                        predicted_change = models[asset.name].predict(X) # Predicted closing price for the next day by the model
                        randomness = np.random.normal(0, min(abs(asset_sequences[asset.name]['DailyChange'].iloc[-1]*2), 11)) # Add random element (rf is deterministic otherwise)

                        predicted_change += randomness
                        new_price = asset_sequences[asset.name]['Close'].iloc[-1] + predicted_change #Predicted price for the next day

                        if new_price <= 0:
                            new_price = 0.000001 #Non-zero prices.
                        values.append(asset.quantity * new_price)

                        new_row = pd.DataFrame({"Open": asset_sequences[asset.name]['Close'].iloc[[-1]], "Close": new_price}) # Wrong assumptionn
                        calc_sequences[asset.name] = pd.concat([calc_sequences[asset.name], new_row], ignore_index=True).iloc[-(look_back*2):]
                        asset_sequences[asset.name] = self.GetAssetFeatures(calc_sequences[asset.name])

                current_portfolio_value = sum(values)
                portfolio_values.append(current_portfolio_value)
            print(f"Simulation {sim} time {datetime.datetime.now() - ts_start}")
            portfolio_futures.append(portfolio_values)

        t_time = datetime.datetime.now() - start
        print(f"Elapsed time: ", {t_time})

        return portfolio_futures

