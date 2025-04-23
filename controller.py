import matplotlib.pyplot as plt
import time
import yfinance as yf

from model import Model
from view import View


class Controller():
    def __init__(self):
        self.Model = Model()

    def GetStarted(self):
        """
        Welcome interface to the user.
        Asks the user which action the user wants to execute
        Calls designated functions. Only ends when the user
        enters 'E' or ctrl+C
        """

        print("Welcome to the portfolio tracker. What do you want to do today?\n")
        option = ''
        valid_options = {'A', 'S', 'V', 'C', 'P'}
        while (option.capitalize() not in valid_options):
            print("\
              (A) add assets to your portfolio\n\
              (S) Show the current and historical price of each asset ticker\n\
              (V) View your current portfolio\n\
              (C) Show calculations and weights\n\
              (P) Perform a simulation\n\
              (E) Exit the application\n")
            option = input("Please, enter your option (letter):\n")
            match option.capitalize():
                case 'A':
                    print('You chose to add assets to your portfolio.\n')
                    self.NewAsset()
                case 'S':
                    print('You chose to show the current and historical price of each asset ticker.\n')
                    self.ShowPrices()
                case 'V':
                    print('You chose to view your current portfolio.\n')
                    self.ViewPortfolio()
                case 'C':
                    print('You chose to show calculations and weights.\n')
                    self.ShowCalculations()
                case 'P':
                    print('You chose to perform a simulation.\n')
                    self.PerformSimulation()
                case 'E':
                    break
                case _:
                    print('That is not a valid option. Enter A, S, V, C or P or E (Exit).\n')
            option = ''
            time.sleep(1)


    def NewAsset(self):
        """
        This function adds a ticker to the model. Validates if the ticker exists (yhfinance)
        and confirms the types of the input (string, etc). Automatically loads asset class
        and sector from yhfinance.
        """
        print("A few questions need to be answered in order to add an asset to your portfolio.")
        ticker = None
        while ticker == None:
            ticker_str = str(input("Please enter a valid ticker: (string)\n"))
            ticker = self.Model.VerifyTicker(ticker_str)
            if ticker is not None:
                break

        print(ticker.info)
        sector = ticker.info.get('sector')
        asset_class = ticker.info.get('assetClass')
        print(f"Sector: {sector}\n")
        print(f"Asset class: {asset_class}\n")

        quantity = -1
        while quantity == -1:
            try:
                quantity = int(input("Quantity: (int)\n"))
            except: 
                print("Please enter an integer")
        price = -1
        while price == -1:
            try:
                price = float(input("Price: (float)\n"))
            except:
                print("Please enter a real number")
        print(f"Now adding to your portfolio:\n\
                ticker: {ticker}\n\
                sector: {sector}\n\
                class: {asset_class}\n\
                quantity: {quantity}\n\
                price: {price}\n")
        _ = self.Model.AddTicker(ticker, sector, asset_class, quantity, price)


    def ShowPrices(self):
        """
        This function plots the data of provided tickers. Tickers can be any (not necessary
        in portfolio). 
        """
        print("This function shows the current and historical prices of each ticker.")
        print("Please, enter the ticker name(s) you want to show. Enter 'C' to continue.")
        tickers = set()
        ticker_str = ''
        while ticker_str.capitalize() != 'C':
            ticker_str = input("Enter a valid ticker, or typ 'C' to continue:\n")
            if ticker_str != 'C':
                if self.Model.VerifyTicker(ticker_str) is not None:
                    tickers.add(ticker_str)
                    print(f"Added {ticker_str} to the infograph")
                else:
                    print("That is not a valid name. Please enter a valid ticker")
        if tickers is not None:
            for ticker in tickers:
                data = self.Model.GetHistoricalData(ticker_str)
                price = self.Model.GetPrice(ticker_str)
                print(price)
                #Add plots
        else:
            print("It seems like you didn't add any valid ticker. Please try again.")


    def ViewPortfolio(self):
        """
        Shows the assets of the user
        """
        print("_______________________________________________________________________________________")
        print("Ticker | Sector | Class | Quantity | Purchase Price | Transaction Value | Current value")
        print("_______|________|_______|__________|________________|___________________|______________")
        for asset in self.Model.GetAssets():
            print(f"{asset.name} | {asset.sector} | {asset.asset_class} | {asset.quantity} | {asset.purchase_price} | - | {asset.GetPrice()}")
        print("_______|________|_______|__________|________________|___________________|______________")


    def ShowCalculations(self):
        """
        Prints calculations for the total portfolio value and the (relative) weights of each asset including
        the option to see the same per asset class and sector.
        """
        print("This function is not implemented yet")
        print("Would you like to see calculations for the value per:\n\
             (A) total portfolio\n\
             (B) asset class\n\
             (C) asset sector\n")
        option = ''
        while option == '':
            option = input("Please enter your choice (A/B/C):\n")
            match option:
                case 'A':
                    calculations = self.Model.GetCalculations('total')
                case 'B':
                    print("Available classes:")
                    print({asset.asset_class for asset in self.Model.GetAssets()})
                    asset_class = input("Please enter the asset class you're interested in:\n")
                    calculations = self.Model.GetCalculations('class', asset_class=asset_class)
                    print(f"Your portfolio over class {asset_class} is constructed as follows:")
                case 'C':
                    print("Available sectors:")
                    print({asset.sector for asset in self.Model.GetAssets()})
                    sector = input("Please enter the sector you're interested in:\n")
                    calculations = self.Model.GetCalculations('sector', sector=sector)
                    print(f"Your portfolio over sector {sector} is constructed as follows:")
        print([item for item in calculations])

    def PerformSimulation(self):
        """
        Performs a simulation with the current portfolio for upcoming 15 years
        Includes 100.000 simulations paths
        """
        self.Model.GetSimulation(100_000, 15)

    
if __name__ == '__main__':
    control = Controller()
    control.GetStarted()