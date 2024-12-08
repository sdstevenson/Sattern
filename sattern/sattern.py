import sattern.get_stock_data as get_stock_data
import sattern.display_stock_data as display_stock_data
from sattern.get_stock_data import history_data
import json

def main():
    print("Hello World from sattern.py")
    data = get_stock_data.load_history_data(period="1y")
    display_stock_data.highlight_pattern(data=data, start_index=100, end_index=500)


if __name__ == "__main__":
    main()