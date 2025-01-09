"""Executes stock trades."""
from typing import Dict

STRONG_SIGNAL_QUANTITY = 10
NORMAL_SIGNAL_QUANTITY = 5

class portfolio():
    def __init__(self, cash: int = 10000, stock: int = 0, display: bool = False):
        self.cash = cash
        self.stock = stock
        self.display = display

    def execute_trade(self, action: str, quantity: int, current_price):
        cost = abs(quantity) * current_price

        if "Buy" in action:
            if cost <= self.cash:
                self.stock += quantity
                self.cash -= cost
            else:
                max_quantity = self.cash // current_price
                if max_quantity > 0:
                    self.stock += max_quantity
                    self.cash -= max_quantity * current_price
                    quantity = max_quantity
        elif "Sell" in action:
            quantity = min(quantity, self.stock)
            if quantity > 0:
                self.stock -= quantity
                self.cash += quantity * current_price
        
        print(f"{action} {quantity} @ {current_price}")

    def __str__(self) -> str:
        return f"Portfolio(cash={self.cash}, stock={self.stock})"