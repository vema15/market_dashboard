2/15/2024:
1) Created functions get_ref_rates(), get_repo_rr_ops(), get_equity_inds(). The first two functions utilize the New York Fed's Markets Data API (https://markets.newyorkfed.org/static/docs/markets-api.html#/), and the last function utilizes the yahoo_fin library to extract stock data. All of the data is converted into a Pandas DataFrame.

2/16/2024
1) Created application architecture through the use of OOP, with one class (AppFunctions) handling the functions and the other (Application) handling the user interface.
2) Created basic while True menu in Application
3) Moved get_ref_rates(), get_repo_rr_ops(), get_equity_inds() to AppFunctions
4) Created agg_dfs() function to concatenate the DataFrames gathered through the aforementioned methods.
5) Created term_print() method in AppFunctions that individually prints out the DataFrames in the user's terminal.