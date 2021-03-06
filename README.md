# TraderBot

This is going to be a fully automated cryptocurrency trading software.
At the present moment it is able to connect to Bittrex.com via its API 1.0. All of the API calls are working and all of their exceptions and errors I could find are handled.
The longest time the program was running without errors was 6 months, then it was stopped manually.

The program runs an infinete loop in main.py where the following sequence is repeated:
1) Collect and manage data (class DataManager)
2) Create buy and sell triggers (class Algorithms)
3) Place and manage orders (class OrderManager)
4) Log balances (class Logging)

There are 3 further main parts of the softwre:
1) Collecting, handling and manipulating historic data (folders HistoricDataHandler, ChartingUtilities)
2) Backtesting (folder BackTesting)
  - this part provides a simulated market environment using historic data where trading algorithms can be tested
3) Online testing (folder OnlineTesting)
  - this part works the same as main.py, but with simulated buy and sell orders
  - the purpose is to test trading algorithms real-time without using money
  
I have developed this software using local git repository, so the previous versoins are not available here.

This software is not ready yet. My plans for the future are:
1) create and test a profitable trading algorithm
  - using trading volume, candlestick charts, trend lines and indicators
  - using machine learning
2) update API handler to the newest API version, create API handlers for more brokers and provide a common interface to them
3) master-slave architecture: the program would run on 2 different servers, and when for some reason the master is not working, the slave would take control
