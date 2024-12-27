import sattern.src.display_stock_data as display_stock_data
from sattern.src.get_stock_data import stock_data
import sattern.src.process_data as process_data

def main():
    # get_stock_data.store_history_data(ticker="ERJ", period="2y")
    test_data = stock_data(ticker="ERJ", period=2)
    display_stock_data.display_stock_price(stock_data=test_data, show=False)
    process_data.predict_next_movement(stock_data=test_data)
    display_stock_data.highlight_pattern(stock_data=test_data)


if __name__ == "__main__":
    main()