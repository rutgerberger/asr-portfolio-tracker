import yfinance as yf
import numpy as np
import matplotlib.pyplot as plt

class Asset():
    def __init__(self, ticker: str, sector: str, asset_class: str, quantity: int, price: float):
        self.name = ticker
        self.ticker = yf.Ticker(ticker)
        self.sector = sector
        self.asset_class = asset_class
        self.quantity = quantity
        self.purchase_price = price

    def GetPrice(self):
        """
        Shorthand for if you wish to get the current price an
        known asset within your portfolio
        """
        return self.ticker.info['currentPrice']


class Model():
    def __init__(self):
        self.assets = set()

    def VerifyTicker(self, ticker: str):
        """
        Checks if the ticker is valid.
        If there is any recent data on the ticker,
        this returns true. False otherwise.
        """
        try:
            tick = yf.Ticker(ticker).history(
                period='1mo')
            return yf.Ticker(ticker)
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
    
    def GetHistoricalData(self, ticker: str, length: str = '1mo'):
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
    
    def GetWeight(self, ticker: str, all_assets: set):
        """
        Calculates the relative weight of the given asset in the
        portfolio
        """
        total_value = 0
        for asset in all_assets:
            if asset.name == ticker:
                asset_value = asset.quantity * asset.GetPrice()
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
                asset_dict = {"ticker": asset.name, "weight": round(self.GetWeight(asset.name, self.assets),3), "value": asset.quantity * asset.GetPrice()}
                calculations.append(asset_dict)
        elif option == 'class':
            for asset in self.assets:
                if asset.asset_class == asset_class:
                    asset_dict = {"ticker": asset.name, "weight": round(self.GetWeight(asset.name, self.assets),3), "value": asset.quantity * asset.GetPrice()}
                    calculations.append(asset_dict)
        elif option == 'sector':
            for asset in self.assets:
                if asset.sector == sector:
                    asset_dict = {"ticker": asset.name, "weight": round(self.GetWeight(asset.name, self.assets),3), "value": asset.quantity * asset.GetPrice()}
                    calculations.append(asset_dict)
        return calculations
    
    def GetPortfolioValue(self):
        """
        Returns the total portfolio value
        """
        total_value = 0
        for asset in self.assets:
            total_value += asset.quantity * asset.GetPrice()
        return total_value
    
    def SimulateReturns(self, mean_returns, cov_matrix, num_simulations, time_steps):
        simulated_returns = np.random.multivariate_normal(
        mean_returns, cov_matrix, size=(num_simulations, time_steps)
        ).T 
        return simulated_returns
    
    def GetSimulation(self, num_simulations, num_years):
        """
        Loads historical data of provided ticker(s). Then, simulates
        the behaviour of the tickers and 
        """
        initial_portfolio_value = self.GetPortfolioValue()
        assets = list(self.assets) #So order is preserved
        weights = [self.getWeight(asset) for asset in assets]

        time_steps = num_years * 252  #Number of trading days * num years
        portfolio_values = np.zeros((num_simulations, time_steps + 1))
        portfolio_values[:, 0] = initial_portfolio_value
        data = yf.download(assets, period='5y') # self.GetHistoryData only accepts strings - this is shorter
        prices = data['Adj Close']
        daily_returns = prices.pct_change().dropna()
        mean_returns = daily_returns.mean()
        cov_matrix = daily_returns.cov()
        simulated_daily_returns = self.SimulateReturns(mean_returns, cov_matrix, num_simulations, time_steps)
        
        for i in range(num_simulations):
            for t in range(time_steps):
                # Calculate portfolio return for this time step
                asset_returns = simulated_daily_returns[:, t, i]
                portfolio_return = np.sum(weights * asset_returns)
                portfolio_values[i, t + 1] = portfolio_values[i, t] * (1 + portfolio_return)

        
        # 6. Analyze and Visualize Results
        final_portfolio_values = portfolio_values[:, -1]

        # Histogram of final portfolio values
        plt.figure(figsize=(10, 6))
        plt.hist(final_portfolio_values, bins=50, density=True, alpha=0.6, color='skyblue')
        plt.title('Distribution of Final Portfolio Values (15 Years, 100,000 Simulations)')
        plt.xlabel('Final Portfolio Value')
        plt.ylabel('Probability Density')
        plt.grid(True)
        plt.show()
        
        # Sample of simulated paths
        plt.figure(figsize=(12, 7))
        num_paths_to_plot = min(50, num_simulations)
        for i in np.random.choice(range(num_simulations), num_paths_to_plot, replace=False):
            plt.plot(portfolio_values[i], alpha=0.1)
        plt.title('Sample of Simulated Portfolio Paths (15 Years)')
        plt.xlabel('Time Step (Days)')
        plt.ylabel('Portfolio Value')
        plt.grid(True)
        plt.show()