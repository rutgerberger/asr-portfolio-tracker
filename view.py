import matplotlib.pyplot as plt

class View():
    def __init__(self):
        plt.figure(figsize=(14, 7))

    def PlotCurrentPrice(self, index, price, label):
        """
        This function adds a horizontal line
        to the plot
        """
        plt.axhline(price, linestyle='--', label=f'Current price {label}')

    def PlotSingleHistory(self, index, data, label):
        plt.plot(index, data['Open'], label=f'{label} - open', alpha=0.7)
        plt.plot(index, data['Close'], label=f'{label} - close', alpha=0.7)
        plt.plot(index, data['High'], label=f'{label} - high', alpha=0.7)
        plt.plot(index, data['Low'], label=f'{label} - low', alpha=0.7)
        plt.title(f'Historical OHLC Prices for {label}')

    def PlotHistoricalData(self, index, data, label):
        """
        This function plots the historical open / close / high / low
        values of each asset
        """
        plt.plot(index, data['Close'], label=f'{label}', alpha=0.7)
        plt.title(f'Historical Closing Prices')

    def Show(self):
        """
        Shows the plot!
        """
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend(loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.show()