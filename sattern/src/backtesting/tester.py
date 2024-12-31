from sattern.src.get_stock_data import stock_data
from sattern.src.process_data import predict_next_movement
from typing import List, Callable

"""tester.py
Backtesting functionality will take place here."""

class backtesting_data:
    def __init__(self, ticker: str, comp_period: int = 10):
        self.ticker: str = ticker
        self.differences: dict = {}
        # comp_period in days
        self.comp_period: int = comp_period

    def direct_comparison(self, test_data: stock_data, actual_stock_data: List[float], method_function: Callable):
        """Direct comparison will occur here. 
        Takes in history_data objects and the method to use to calculate data."""
        method_function(stock_data=test_data)

        difference_sum: float = 0.0

        for i in range(int(self.comp_period*7.5)):
            difference_sum += test_data.comp.predicted_prices[i] - actual_stock_data[i]

        return difference_sum/(self.comp_period*7.5)

    def multi_period_compare(self, period: int = 2, method_function: Callable = predict_next_movement):
        """Call direct_comparison over various periods of time.
        Track performance vs data given and stores relevant data."""

        test_data = stock_data(ticker=self.ticker, period=period)

        # Create an entry in the differences dict holding 
        self.differences[method_function.__name__] = {}

        # Compare prediction to actual stock movement, assuming comp_period is 10 days
        data_len: int = int(self.comp_period*7.5)        # Length of data given to compare (in days)
        temp_stock_data = stock_data(ticker=test_data.ticker, period=test_data.period)


        # Test various data lengths, multiplying data length by 1.5 each time
        while (data_len + self.comp_period*7.5) < len(test_data.close):
            # Trim stock_data to only contain the period we want
            temp_stock_data.close = test_data.close.copy()[: data_len]
            temp_stock_data.date = test_data.date.copy()[: data_len]

            # And extract what the stock after this actually was
            actual_stock_data = test_data.close.copy()[data_len : data_len + int(self.comp_period*7.5)]
            # print(f"Actual: {len(actual_stock_data)}\n{actual_stock_data}")

            self.differences[method_function.__name__][data_len] = self.direct_comparison(
                test_data=temp_stock_data, 
                actual_stock_data=actual_stock_data, 
                method_function=method_function
            )

            data_len = int(data_len * 1.5)

        print(self.differences)


def multi_stock_compare(stocks: List[str]):
    """Call multi_period_compare for multiple stocks
    and return the overall result."""
    pass