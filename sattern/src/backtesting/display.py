from sattern.src.display_stock_data import display_stock_price
from sattern.src.get_stock_data import history_data
from sattern.src.backtesting.tester import backtesting_data
from matplotlib import pyplot

def plot_comparison(base_data: history_data, backtesting_data: backtesting_data, show: bool = True):
    """
    Plot base data and overlay comparison data
    """
    # Get base plot
    fig, ax = display_stock_price(base_data, show=False)
    
    # Plot comparison data
    comparison_data = backtesting_data['']
    comparison_x = range(len(comparison_data.date))
    ax.plot(comparison_x, comparison_data.close, color='red', alpha=0.7, 
            label='Comparison Period')
    
    # Add legend
    ax.legend()
    
    if show:
        pyplot.show()
        
    return fig, ax