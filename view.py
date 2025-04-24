import matplotlib.pyplot as plt

class View():
    def __init__(self, title: str, xlabel: str, ylabel: str, legend: bool = True):
        plt.figure(figsize=(14, 7))
        plt.xlabel(xlabel)
        plt.ylabel(ylabel)
        plt.title(title)
        self.legend = legend

    def PlotCurrentPrice(self, index, price, label):
        """
        This function adds a horizontal line
        to the plot
        """
        plt.axhline(price, linestyle='--', label=f'Current price {label}')

    def PlotSingleHistory(self, index, data, label):
        plt.plot(index, data['Open'], label='Open', alpha=0.7)
        plt.plot(index, data['Close'], label=f'Close', alpha=0.7)
        plt.plot(index, data['High'], label=f'High', alpha=0.7)
        plt.plot(index, data['Low'], label=f'Low', alpha=0.7)
        plt.title(f'Historical OHLC Prices for {label}')

    def PlotData(self, index, data, label):
        """
        This function plots the historical open / close / high / low
        values of each asset
        """
        plt.plot(index, data, label=f'{label}', alpha=0.7)

    def Show(self):
        """
        Shows the plot!
        """
        if self.legend:
            plt.legend(loc='upper left')
        plt.grid(True)
        plt.tight_layout()
        plt.show()