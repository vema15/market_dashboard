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
10) Created rudimentary xlsx_export() method that converts the raw DataFrames into an Excel file under the sheets folder

2/18/2024
1) Created alternative API call to NY Fed for get_repo_rr_ops() method in order to reduce the likelihood of a blank DataFrame being returned
2) Created call_tests folder containing ct.py, which tests the effectiveness of various API calls (Note: This file is solely for troubleshooting and is not part of the overall application structure)
3) Created visualizer() method in the AppFunctions class using matplotlib (pyplot) module. The method opens a windows containing three windows w/ equity, repo/reverse repo, and reference rate data. Added method to the program_run method in the Application class.
4) Fixed bug in the remove_files() method that caused the message, "Your file was successfully removed" to be printed regardless of the actual success of the removal.
5) Created an 'all' option in the remove_files() method to allow the user to simultaneosly remove the stored .xlsx and .csv files.
6) Added titles to the tables shown in the visualizer() method

2/26/2024
1) Updated the user menu to reflect new options
2) Created the outline for the gen_mkt_update() method in the AppFunctions class
3) Wrote the script for the market report in the gen_mkt_update() method
4) Made the script within the gen_mkt_update() responsive to the output of varying API calls
5) Created failsafe for the gen_mkt_update() in case any of the data sourced from the APIs fail

2/27/2024
1) Changed AppFunctions class to MktAppFunctions to accomodate future classes
2) Changed Application class to UserInterface class in order to reflect the class's true function
3) Changed ui_run method in the UserInferface class to the mkt_ui_run method to make room for the future econ_ui_run method (Econ. data menu)
4) Moved the contents of the the old main class into the new Application class
5) Created econ_ui_run method in the UserInterface class
6) Created menu_select method that acts as a master access menu (while True) for the markets and economy classes and their methods in the Application class 

2/28/2024
1) Created several methods in the EconAppFunctions class to fetch different categories of economic data series from the FRED API.

2/29/2024
1) Added indicator name, units, and data intervals to each item in the the series_ids dictionaries in the EconAppFunctions fetching methods
2) Created master menu for the economic data
3) Created submenu in the UserInterface class to access the categorical economic data series methods created in the EconAppFunctions class
4) Got rid of the methods that house the series ids and created a single agg_category() method to aggregate to the data in order to reduce redundancy. Placed the ids in the initializer method instead.
5) agg_category() method now returns a Pandas Dataframe with the columns '|Indicator|', '|Units|', '|Release Interval|', '|Latest Release Date|', '|Latest Release Value|', '|Penultimate Release Date|', '|Penultimate Release Value|', '|Percent Change between Periods|'.
6) Added minor aesthetic tweaks to the menu layouts (turned them into center-aligned boxes)
7) Added an extra catch in order to prevent the menus from immediately crowding the terminal after a query is entered.

********Beta 1.0 Complete************

3/2/2024
1) Began writing out the script for the econ_report() method in the EconApplications class.
2) Created the exp_cont_inc_dec() function within the econ_report class to house the conditionals required to discern an expansion, contraction, increase, or decrease in the script.
3) Converted all of the print lines in the econ_report into a text list (for future application development).
4) Finished the report section of the econ_report() method (still needs appendix).