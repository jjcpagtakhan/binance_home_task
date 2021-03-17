# Binance Home Task
## About The Project
This contains the script written in Python to answer the following home task:

1. Print the top 5 symbols with quote asset BTC and the highest volume over the last 24 hours in descending order.
2. Print the top 5 symbols with quote asset USDT and the highest number of trades over the last 24 hours in descending order.
3. Using the symbols from Q1, what is the total notional value of the top 200 bids and asks currently on each order book?
4. What is the price spread for each of the symbols from Q2?
5. Every 10 seconds print the result of Q4 and the absolute delta from the previous value for each symbol.
6. Make the output of Q5 accessible by querying http://localhost:8080/metrics using the Prometheus Metrics format.

## Pre-requisite
This has been tested using Ubuntu20 LTS OS. The following should be installed in the system:

1. Python3
2. Pip3
```
sudo apt install -y python3-pip
```
3. Install requirements.txt
```
pip3 install -r requirements.txt
```

## Usage
Instruction on how to run the script.
```
python3 client.py
```

## To Do / Next Steps
- Unit tests
- Handling of exceptions
- Script to accept parameters to run specific function