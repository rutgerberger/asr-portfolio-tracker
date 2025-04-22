from model import Model
from view import View

import pandas as pd
import time

class Controller():
    def __init__(self):
        pass

    def getStarted(self):
        """
        Welcome interface to the user.
        Asks the user which action the user wants to execute
        """

        print("Welcome to the portfolio tracker. What do you want to do today?\n")
        print("\
              (A) add assets to your portfolio\n\
              (S) Show the current and historical price of each asset ticker\n\
              (V) View your current portfolio\n\
              (C) Show calculations and weights\n\
              (P) Perform a simulation\n")
        time.sleep(1)
        option = ''
        valid_options = {'A', 'S', 'V', 'C', 'P'}
        while (option.capitalize() not in valid_options):
            option = input("Please, enter your option (letter):\n")
            match option.capitalize():
                case 'A':
                    print('You chose to add assets to your portfolio')
                case 'S':
                    print('You chose to show the current and historical price of each asset ticker')
                case 'V':
                    print('You chose to view your current portfolio')
                case 'C':
                    print('You chose to show calculations and weights')
                case 'P':
                    print('You chose to perform a simulation')
                case _:
                    print('That is not a valid option. Enter A, S, V, C or P')

    
if __name__ == '__main__':
    control = Controller()
    control.getStarted()