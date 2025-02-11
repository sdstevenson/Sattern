"""Executes stock trades."""
from typing import Dict, Union, List, Tuple

class portfolio():
    def __init__(self, cash: int = 10000, stock: int = 0, display: bool = False, enable_shorting: bool = False):
        self.cash = cash
        self.stock = stock
        self.display = display
        self.enable_shorting = enable_shorting
        self.short_positions: Dict[float, int] = {}
        self.short_stock = 0

        print(f"Init portfolio with {cash} cash and {stock} stock. Options: display={display}, enable_shorting={enable_shorting}")

    def execute_trade(self, action: Union[Dict, str], current_price: float, quantity: int = None) -> int:
        if isinstance(action, dict):
            action = combine_signals(action, current_price)
        # Set the amounts to buy
        strong_signal_quantity = 10000//current_price//2
        normal_signal_quantity = strong_signal_quantity//4
        if action == "Strong Buy" or action == "Strong Sell":
            quantity = strong_signal_quantity
        elif action == "Buy" or action == "Sell":
            quantity = normal_signal_quantity
        else:
            quantity = 0

        if "Buy" in action:
            if self.enable_shorting:
                # Get rid of all short positions
                for entry_price, short_quantity in list(self.short_positions.items()):
                    profit = short_quantity * (entry_price - current_price)
                    self.cash += short_quantity * current_price
                    self.short_stock -= short_quantity
                    if self.display:
                        if profit < 0:
                            print(f"\tClosing short position {short_quantity} @ {current_price} for a loss of {profit:.2f}")
                        else:
                            print(f"\tClosing short position {short_quantity} @ {current_price} for a profit of {profit:.2f}")
                    self.short_positions.pop(entry_price)
                if self.short_stock != 0 or self.short_positions != {}:
                    raise ValueError("Error: Short positions not cleared.")

            # Limit num buy shares by available cash
            if self.cash < 0:
                raise ValueError("Error: Negative cash balance.")
            tradeable_qty = min(quantity, self.cash // current_price)
            self.stock += tradeable_qty
            self.cash -= tradeable_qty * current_price
            if self.display:
                print(f"\tOpened buy position {tradeable_qty} @ {current_price}")

        elif "Sell" in action:
            sell_qty = quantity  # treat quantity as the intended number of shares to sell (a positive number)
            # Sell all available long positions first.
            long_sell_qty = min(sell_qty, self.stock)
            self.stock -= long_sell_qty
            self.cash += long_sell_qty * current_price
            if self.display and long_sell_qty > 0:
                print(f"\tClosing buy position {long_sell_qty} @ {current_price}")

            # If the order is larger than your long position and shorting is enabled
            remainder = sell_qty - long_sell_qty
            if remainder > 0 and self.enable_shorting:
                # At max, 50% of portfolio value can be shorted.
                if self.short_stock + remainder > self.total_value(current_price) // 3:
                    remainder = self.total_value(current_price) // 3 - self.short_stock
                if remainder > 0:
                    # Record the short position by the current price.
                    self.short_positions[current_price] = self.short_positions.get(current_price, 0) + remainder
                    self.short_stock += remainder
                    self.cash -= remainder * current_price
                    if self.display:
                        print(f"\tOpened short position {remainder} @ {current_price}")

        return action, quantity

    def total_value(self, current_price: float) -> float:
        short_value = 0
        for entry_price, short_quantity in self.short_positions.items():
            short_value += short_quantity * (entry_price - current_price) + short_quantity * current_price
        return self.cash + self.stock * current_price + short_value

    def __str__(self) -> str:
        return f"Portfolio(cash={self.cash:.2f}, stock={self.stock})"

def combine_signals(actions: Dict, curr_price: float) -> str:
    # Set the amounts to buy
    num_metrics = 0
    metric_avg = 0

    for metric in actions.keys():
        num_metrics += 1
        metric_action = actions[metric]
        if metric_action == "Strong Buy":
            metric_avg += 1
        elif metric_action == "Buy":
            metric_avg += 0.5
        elif metric_action == "Sell":
            metric_avg -= 0.5
        elif metric_action == "Strong Sell":
            metric_avg -= 1

    metric_avg /= num_metrics
    if metric_avg >= 0.8:
        action = "Strong Buy"
    elif metric_avg >= 0.25:
        action = "Buy"
    elif metric_avg > -0.25:
        quantity = 0
        action = "Hold"
    elif metric_avg > -0.8:
        action = "Sell"
    else:
        action = "Strong Sell"

    if False:
        string = ""
        for metric in actions.keys():
            string += f"{metric}: {actions[metric]}"
        print(f"\t{action} {quantity} -- Individual Actions: {string}\n")

    return action