import sattern.src.tools.api as api 
from sattern.src.metrics.sattern import sattern
from sattern.src.tools.display import display

def run_sattern(ticker: str = "ERJ"):
    period = 10
    max_diff = 5
    financial_metrics = api.get_financial_metrics(ticker=ticker)
    financial_metrics, decision = sattern(financial_metrics=financial_metrics, period=period, max_diff=max_diff)
    # print(f"{financial_metrics}\n***{decision}***")
    display(data=financial_metrics, metrics_to_plot=["prices", "sattern", "sattern_highlight"], ticker=ticker, max_diff=max_diff)
    return financial_metrics, decision

def main():
    run_sattern(ticker="ERJ")

if __name__ == "__main__":
    main()