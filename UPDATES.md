2/15/2024:
1) Created functions get_ref_rates(), get_repo_rr_ops(), get_equity_inds(). The first two functions utilize the New York Fed's Markets Data API (https://markets.newyorkfed.org/static/docs/markets-api.html#/), and the last function utilizes the yahoo_fin library to extract stock data. All of the data is converted into a Pandas DataFrame.

2/16/2024
1) Created application architecture through the use of OOP, with one class (AppFunctions) handling the functions and the other (Application) handling the user interface.
2) Created basic while True menu in Application
3) Moved get_ref_rates(), get_repo_rr_ops(), get_equity_inds() to AppFunctions
4) Created agg_dfs() method to concatenate the DataFrames gathered through the aforementioned methods.
5) Created term_print() method in AppFunctions that individually prints out the DataFrames in the user's terminal.
6) Created csv_export() method in AppFunctions that takes the aggregated DataFrames and exports them as a .csv file in the csv_files folder
7) Created file_remove() method in AppFunctions that can clean the csv folder or clear the sheet folder of raw excel sheets. Note: Both the Excel and the CSV files are overwritten, so the purpose of this function is solely to get rid of the files and not to reduce clutter
8) Created loading screen in main() function
9) Modified print output formatting for term_print() method