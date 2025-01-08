import sattern.src.tools.api as api 
from sattern.src.metrics.sattern import sattern
from sattern.src.tools.display import display
from sattern.src.tools.llm import run_llm

def run_sattern(ticker: str = "ERJ"):
    period = 10
    max_diff = 5
    financial_metrics = api.get_financial_metrics(ticker=ticker)
    financial_metrics, decision = sattern(financial_metrics=financial_metrics, period=period, max_diff=max_diff)
    # print(f"{financial_metrics}\n***{decision}***")
    display(data=financial_metrics, metrics_to_plot=["prices", "sattern", "sattern_highlight"], ticker=ticker, max_diff=max_diff)
    return financial_metrics, decision

def run_trader(ticker: str = "ERJ"):
    period = 10
    max_diff = 5
    financial_metrics = api.get_financial_metrics(ticker=ticker)
    financial_metrics, decision = sattern(financial_metrics=financial_metrics, period=period, max_diff=max_diff)
    # display(data=financial_metrics, metrics_to_plot=["prices", "sattern", "sattern_highlight"], ticker=ticker, max_diff=max_diff)

    data = {
        "ticker": ticker,
        "prices": financial_metrics["prices"].dropna(),
        "sattern_highlight": financial_metrics["sattern_highlight"].dropna(),
        "sattern": financial_metrics["sattern"].dropna(),
        "sattern_action": decision
    }

    run_llm(data)

    return financial_metrics, decision

def main():
    run_trader()
    # run_sattern(ticker="ERJ")

if __name__ == "__main__":
    main()