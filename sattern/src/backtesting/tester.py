from sattern.src.get_stock_data import history_data, load_history_data
from sattern.src.process_data import extracted_data, extract_curves, predict_next_movement
from typing import List, Callable

"""tester.py
Backtesting functionality will take place here."""

class backtesting_data:
    def __init__(self, ticker: str, comp_period: int = 10):
        self.ticker: str = ticker
        self.differences: dict = {}
        # comp_period in days
        self.comp_period: int = comp_period

    def direct_comparison(self, stock_data: history_data, actual_stock_data: List[float], method_function: Callable):
        """Direct comparison will occur here. 
        Takes in history_data objects and the method to use to calculate data."""
        extracted_stock_data = extract_curves(data=stock_data)
        next_dates, next_movement = method_function(data=stock_data, extracted_data=extracted_stock_data)

        difference_sum: float = 0.0

        for i in range(int(self.comp_period*7.5)):
            difference_sum += next_movement[i] - actual_stock_data[i]

        return difference_sum/(self.comp_period*7.5)

    def multi_period_compare(self, period: int = 2, method_function: Callable = predict_next_movement):
        """Call direct_comparison over various periods of time.
        Track performance vs data given and stores relevant data."""

        stock_data = load_history_data(ticker=self.ticker, period=period)

        # Create an entry in the differences dict holding 
        self.differences[method_function.__name__] = {}

        # Compare prediction to actual stock movement, assuming comp_period is 10 days
        data_len: int = int(self.comp_period*7.5)        # Length of data given to compare (in days)
        test_stock_data = history_data()


        while (data_len + self.comp_period*7.5) < len(stock_data.close):
            # Trim stock_data to only contain the period we want
            test_stock_data.ticker = stock_data.ticker
            test_stock_data.ticker = stock_data.ticker
            test_stock_data.period = stock_data.period
            test_stock_data.close = stock_data.close.copy()[: data_len]
            test_stock_data.date = stock_data.date.copy()[: data_len]

            # And extract what the stock after this actually was
            actual_stock_data = stock_data.close.copy()[data_len : data_len + int(self.comp_period*7.5)]
            # print(f"Actual: {len(actual_stock_data)}\n{actual_stock_data}")

            self.differences[method_function.__name__][data_len] = self.direct_comparison(
                stock_data=test_stock_data, 
                actual_stock_data=actual_stock_data, 
                method_function=method_function
            )

            data_len *= 2

        print(self.differences)


def multi_stock_compare(stocks: List[str]):
    """Call multi_period_compare for multiple stocks
    and return the overall result."""
    pass