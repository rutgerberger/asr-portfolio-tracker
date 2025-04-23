import time

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

        print("Welcome to the portfolio tracker. What do you want to do today?")
        option = ''
        valid_options = {'A', 'S', 'V', 'C', 'P'}
        while (option.capitalize() not in valid_options):
            print("\n\
              (A) add assets to your portfolio\n\
              (S) Show the current and historical price of asset tickers\n\
              (V) View your current portfolio\n\
              (C) Show calculations and weights of your portfolio\n\
              (P) Perform a simulation\n\
              (E) Exit the application\n")
            option = input("Please, enter your option (letter):\n")
            match option.capitalize():
                case 'A':
                    print('You chose to add assets to your portfolio.\n')
                    self.NewAsset()
                case 'S':
                    print('You chose to show the current and historical price of asset tickers.\n')
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
        #Retrieves ticker info
        sector = ticker.info.get('sector')
        asset_class = ticker.info.get('typeDisp')
        print(f"Sector: {sector}")
        print(f"Asset class: {asset_class}")
        #Now we define how many and for how much
        price = -1
        while price == -1:
            try:
                price = float(input("Please enter the purchase price you want to buy for: (float)\n"))
            except:
                print("Please enter a real number")
        quantity = -1
        while quantity == -1:
            try:
                quantity = int(input("Please enter the desired quantity: (int)\n"))
            except: 
                print("Please enter an integer")

        #Confirmation
        print(f"Now adding to your portfolio:\n\
                ticker: {ticker_str}\n\
                sector: {sector}\n\
                class: {asset_class}\n\
                quantity: {quantity}\n\
                price: {price}\n")
        self.Model.AddTicker(ticker_str, sector, asset_class, quantity, price)


    def ShowPrices(self):
        """
        This function plots the data of provided ticker(s). Tickers can be any (not necessary
        in portfolio).
        """
        print("This function shows the current and historical prices of tickers.")
        print("Do you want to\n\
              (A) show all tickers in your portfolio, or\n\
              (B) enter the ticker name(s) you want to show.")
        choice = input("")
        if choice.capitalize() == 'B':
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
        else:
            tickers = {asset.name for asset in self.Model.GetAssets()}
        print(tickers)
        if tickers is not None:
            plot = View() # Create view object
            for ticker_str in tickers:
                data = self.Model.GetHistoricalData(ticker_str)
                price = self.Model.GetPrice(ticker_str)
                plot.PlotCurrentPrice(data.index, price, ticker_str)
                if len(tickers) > 1:
                    plot.PlotHistoricalData(data.index, data, ticker_str)
                else:
                    plot.PlotSingleHistory(data.index, data, ticker_str)
            plot.Show()
        else:
            print("It seems like you didn't add any valid ticker. Please try again.")


    def ViewPortfolio(self):
        """
        Shows the assets of the user
        """
        print("________________________________________________________________________________________________")
        print(f"{'Ticker':<8} | {'Sector':<10} | {'Class':<7} | {'Quantity':>8} | {'Purchase Price':>14} | {'Transaction Value':>17} | {'Current value':>13}")
        print("_________|____________|_________|__________|________________|___________________|_______________")
        for asset in self.Model.GetAssets():
            transaction_value = asset.quantity * asset.purchase_price
            current_value = asset.quantity * asset.GetPrice()
            print(f"{asset.name:<8} | {asset.sector:<10} | {asset.asset_class:<7} | {asset.quantity:>8} | {asset.purchase_price:>14.2f} | {transaction_value:>17.2f} | {current_value:>13.2f}")
        print("_________|____________|_________|__________|________________|___________________|_______________")


    def ShowCalculations(self):
        """
        Prints calculations for the total portfolio value and the (relative) weights of each asset including
        the option to see the same per asset class and sector.
        """
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
                    total_value = self.Model.GetPortfolioValue(option='total')
                    print(f"Your portfolio is worth {round(total_value,3)} and is constructed as follows:")
                case 'B':
                    print("Available classes:")
                    print({asset.asset_class for asset in self.Model.GetAssets()})
                    asset_class = input("Please enter the asset class you're interested in:\n")
                    calculations = self.Model.GetCalculations('class', asset_class=asset_class)
                    total_value = self.Model.GetPortfolioValue(option='class', label=asset_class)
                    print(f"Your portfolio over class {asset_class} is worth {round(total_value,3)} and is constructed as follows:")
                case 'C':
                    print("Available sectors:")
                    print({asset.sector for asset in self.Model.GetAssets()})
                    sector = input("Please enter the sector you're interested in:\n")
                    calculations = self.Model.GetCalculations('sector', sector=sector)
                    total_value = self.Model.GetPortfolioValue(option='sector', label=sector)
                    print(f"Your portfolio over sector {sector} is worth {round(total_value,3)} and is constructed as follows:")
        for item in calculations:
            print(item)

    def PerformSimulation(self):
        """
        Performs a simulation with the current portfolio for upcoming 15 years
        Includes 100.000 simulations paths
        """
        self.Model.SimulatePortfolio(100_000, 15, 60)

    
if __name__ == '__main__':
    control = Controller()
    control.GetStarted()