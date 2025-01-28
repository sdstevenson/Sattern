"""Executes stock trades."""
from typing import Dict, Union

class portfolio():
    def __init__(self, cash: int = 10000, stock: int = 0, display: bool = False):
        self.cash = cash
        self.stock = stock
        self.display = display

    def execute_trade(self, action: Union[Dict, str], current_price: float, quantity: int = None, show: bool = False):
        if quantity is None or type(action) == Dict:    # Quantity will only be none if action is a Dict
            # Set the amounts to buy
            strong_signal_quantity = 10000//current_price
            normal_signal_quantity = strong_signal_quantity//2
            num_metrics = 0
            metric_avg = 0
            for metric in action.keys():
                num_metrics += 1
                metric_action = action[metric]["action"]
                if metric_action == "Strong Buy":
                    metric_avg += 1
                elif metric_action == "Buy":
                    metric_avg += 0.5
                elif metric_action == "Sell":
                    metric_avg -= 0.5
                elif metric_action == "Strong Sell":
                    metric_avg -= 1
            if metric_avg >= 0.8:
                quantity = strong_signal_quantity
                action = "Strong Buy"
            elif metric_avg >= 0.1:
                quantity = normal_signal_quantity
                action = "Buy"
            elif metric_avg > -0.1:
                quantity = 0
                action = "Hold"
            elif metric_avg > -0.8:
                quantity = -1 * normal_signal_quantity
                action = "Sell"
            else:
                quantity = -1 * strong_signal_quantity
                action = "Strong Sell"

        cost = abs(quantity) * current_price

        if "Buy" in action and cost > self.cash:
            quantity = self.cash // current_price
        elif "Sell" in action:
            quantity = -1 * abs(min(abs(quantity), self.stock))

        self.stock += quantity
        self.cash -= quantity * current_price

        if show:
            print(f"{action} {quantity} @ {current_price}")

    def __str__(self) -> str:
        return f"Portfolio(cash={self.cash:.2f}, stock={self.stock})"