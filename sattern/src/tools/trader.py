"""Executes stock trades."""
from typing import Dict

STRONG_SIGNAL_QUANTITY = 10
NORMAL_SIGNAL_QUANTITY = 5

class portfolio():
    def __init__(self, cash: int = 10000, stock: int = 0, display: bool = False):
        self.cash = cash
        self.stock = stock
        self.display = display

    def execute_trade(self, action: str, current_price: float, quantity: int = None, show: bool = False):
        if quantity is None:
            if action == "Strong Buy":
                quantity = STRONG_SIGNAL_QUANTITY
            elif action == "Buy":
                quantity = NORMAL_SIGNAL_QUANTITY
            elif action == "Strong Sell":
                quantity = STRONG_SIGNAL_QUANTITY
            elif action == "Sell":
                quantity = NORMAL_SIGNAL_QUANTITY
            else:
                quantity = 0


        cost = abs(quantity) * current_price

        if "Buy" in action and cost > self.cash:
            quantity = self.cash // current_price
        elif "Sell" in action:
            quantity = abs(min(abs(quantity), self.stock))
            quantity = quantity * -1

        self.stock += quantity

        if show:
            print(f"{action} {quantity} @ {current_price}")

    def __str__(self) -> str:
        return f"Portfolio(cash={self.cash}, stock={self.stock})"