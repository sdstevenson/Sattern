import sattern.get_stock_data as get_stock_data
import sattern.display_stock_data as display_stock_data
from sattern.get_stock_data import history_data
import sattern.process_data as process_data
import json

def main():
    # get_stock_data.store_history_data(ticker="MSFT", period="1y")
    data = get_stock_data.load_history_data(ticker="AAPL", period="1y")
    # start_test = [0, 1500]
    # end_test = [10, 1700]
    # display_stock_data.display_stock_price(data=data)
    extracted_data = process_data.extract_curves(data=data)
    display_stock_data.highlight_pattern(data=data, start_indicies=extracted_data.start_indicies, end_indicies=extracted_data.end_indicies)


if __name__ == "__main__":
    main()