import sattern.get_stock_data as get_stock_data
import json

def main():
    print("Hello World from sattern.py")
    # get_stock_data.store_history_data(save_to_file=True)
    print(json.dumps(get_stock_data.load_data_from_file(), indent=1))


if __name__ == "__main__":
    main()