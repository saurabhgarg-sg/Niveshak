import random

import numpy as np
import talib

# Generate a list of 100 pseudo-random "closing prices"
random.seed(42)  # For reproducible results
close_prices = [random.random() * 100 for _ in range(100)]

# Compute a 10-period Simple Moving Average using TA-Lib
sma_10 = talib.SMA(np.array(close_prices), timeperiod=10)

print("Last 10 closing prices:")
print(close_prices[-10:])

print("\nLast 10 values of the 10-period SMA:")
print(sma_10[-10:])
