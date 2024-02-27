import requests as rq
import pandas as pd
import numpy as np
from yahoo_fin import stock_info as si
import os
import matplotlib.pyplot as plt
from datetime import datetime

#MASTER FUNCTIONS
class AppFunctions:
    def __init__(self) -> None:
        self.master_frames = [AppFunctions.get_ref_rates(), AppFunctions.get_repo_rr_ops(), AppFunctions.get_equity_inds()]
        #UPDATE data_names whenever new information pulling methods are added
        self.data_names = [
            "Reference Rates",
            "Repo/Reverse Repo Rates",
            "Equity Index (ETF) Values"
        ]
    
    #**RAW DATAFRAMES**

    #Important Ref Rates Info
    def get_ref_rates():
        rates_url = "https://markets.newyorkfed.org//api/rates/all/latest.json"
        rates_response = rq.get(rates_url)
        rates_json = rates_response.json()
        try:
            rates_df = pd.DataFrame(rates_json['refRates'])[['effectiveDate', 'type', 'percentRate']]
            rates_df = rates_df.rename(columns={'effectiveDate': 'Date', 'type': 'Rate Type', 'percentRate': 'Rate (%)'})
            select_rates_df = rates_df.iloc[1:,:]
            return select_rates_df
        except:
            return pd.DataFrame(["No Data Available for Reference Rates"])

    #Repo / Reverse Repo Ops
    def get_repo_rr_ops():
        repo_rate_url = "https://markets.newyorkfed.org//api/rp/all/all/results/latest.json"
        repo_rate_response = rq.get(repo_rate_url)
        repo_rate_json = repo_rate_response.json()
        try:
            base_url = "https://markets.newyorkfed.org"
            ltw = "/api/rp/all/all/results/lastTwoWeeks.json"
            repo_rate_url = base_url+ltw
            repo_rate_response = rq.get(repo_rate_url)
            repo_rate_json = repo_rate_response.json()
        except:
            print("No data available, trying other sources...", end='\r')
            try:
                repo_rate_url = "https://markets.newyorkfed.org//api/rp/all/all/results/latest.json"
                repo_rate_response = rq.get(repo_rate_url)
                repo_rate_json = repo_rate_response.json()
            except:
                return pd.DataFrame(["No Data Available for Repos/Reverse Repos"])

        rr, r = pd.DataFrame(repo_rate_json['repo']['operations'][0])[['operationType', 'operationDate', 'maturityDate','details']], pd.DataFrame(repo_rate_json['repo']['operations'][1])[['operationType', 'operationDate', 'maturityDate', 'details']]
        rr_desired_details = rr['details'].values[0]['securityType'], rr['details'].values[0]['percentOfferingRate']
        r_desired_details = r['details'].values[0]['securityType'], r['details'].values[0]['minimumBidRate']
        rr['Type'] = rr_desired_details[0]
        rr['Rate'] = rr_desired_details[1]
        r['Type'] = r_desired_details[0]
        r['Rate'] = r_desired_details[1]
        agg_rr_r_df = pd.concat([r,rr])
        agg_rr_r_df.drop(columns='details', inplace=True)
        agg_rr_r_df.rename(columns={'operationType': 'Operation Type', 'operationDate': 'Operation Date', 'maturityDate': 'Maturity Date'}, inplace=True)
        return agg_rr_r_df[['Operation Date', 'Operation Type', 'Type', 'Rate', 'Maturity Date']]

    #Equity Indices
    def get_equity_inds():
        tickers = [('SPY', 'S&P 500 (ETF)'), 
                   ('QQQ', 'NASDAQ 100 (ETF)'), 
                   ('DIA', 'DJIA (ETF)')]
        index_dfs = []
        try:
            for ticker in tickers:
                ind_df = si.get_data(ticker[0]).iloc[-1, :]
                ind_df['Date'] = ind_df.name
                ind_df.name = ticker[1]
                ind_df.rename({'open': 'Open', 'high': 'High', 'low':'Low', 'close': 'Close', 'volume':'Volume', 'ticker': 'Ticker'}, inplace=True)
                index_dfs.append(pd.DataFrame(ind_df).T)
            total_ind_dfs = pd.concat(index_dfs)
            total_ind_dfs.drop(columns=['adjclose', 'High', 'Low'], inplace=True)
            return total_ind_dfs[['Date', 'Ticker', 'Open', 'Close', 'Volume']]
        except:
            return pd.DataFrame(["No Data Available for Equity Indices"])
        
    #**SYNTHESIZED DATAFRAMES**

    #Get frames
    def agg_dfs(self):
        return pd.concat(self.master_frames)
    
    #**DATA OUTPUT**
    
    #Visualizer (Option 1)
    def visualizer(self):
        sep_tables = self.master_frames
        fig, ax = plt.subplots(3, 1)
        fig.patch.set_visible(False)
        for i in range(len(sep_tables)):
            col = sep_tables[i].columns
            celltext = sep_tables[i].values
            ax[i].axis('off')
            ax[i].axis('tight')
            ax[i].table(cellText = celltext, colLabels = col, loc = 'center')
            ax[i].set_title(self.data_names[i], color='white')
        fig.tight_layout()
        plt.show()

    #Terminal Print (Option 2)
    def term_print(self):
        table_titles = ['Reference Rates', 'Repo/Reverse Repo Rates', 'Equity Indices']
        for i in range(len(self.master_frames)):
            print(f'{"*"*3}{table_titles[i]}{"*"*3}')
            print(self.master_frames[i])
            print()
    
    #Generate Report (Option 3):
    def gen_mkt_report(self):
        try:
            print(f"Hello, and welcome to the Daily Market Report (as of {datetime.today()}).")
            print(f"*** Note: If the current time is earlier than 4PM EST (NYSE market close), the equity indices' figures are from the previous day. ***")
            print("Starting off with the equity indices,", end=" ")
            close_status = {}
            close_types = ["down", "up", "flat"]
            for row in list(self.master_frames[2].iterrows()):
                if row[1]['Open'] > row[1]['Close']:
                    close_status[row[0]] = close_types[0]
                elif row[1]['Open'] < row[1]['Close']:
                    close_status[row[0]] = close_types[1]
                elif row[1]['Open'] == row[1]['Close']:
                    close_status[row[0]] = close_types[2]
            absolute_close = False
            for i in close_types:
                if list(close_status.values()).count(i) == 3:
                    print(f"all of the major U.S. equity indices closed {i} today.")
                    absolute_close = True
            if absolute_close == False:
                counter = 1
                for key, value in close_status.items():
                    if counter == 0:
                        print(f"The {key} index closed {value},", end=" ")
                    elif counter == len(close_status):
                        print(f"and the {key} index closed {value}.")
                    else:
                        print(f"the {key} index closed {value},", end=" ")
                    counter += 1
            repo_info = list(self.master_frames[1].iterrows())
            print(f"Switching over to rates, the FED's Treasury-backed overnight reverse repo rate is sitting at {repo_info[-1][1]['Rate']} percent, and its Treasury-backed repo rate is sitting at {repo_info[0][1]['Rate']} percent.")
            print(f"This is showing a spread of {float(float(repo_info[0][1]['Rate']) - float(repo_info[-1][1]['Rate'])):.2f} percent for the FED.")
            ref_rates_info = list(self.master_frames[0].iterrows())
            rates_range = (min([row[1]["Rate (%)"] for row in ref_rates_info]), max([row[1]["Rate (%)"] for row in ref_rates_info]))
            print(f"Reference rates are sitting in the range of {rates_range[0]} to {rates_range[1]} percent, with", end=" ")
            counter = 1
            for row in ref_rates_info:
                if counter == len(ref_rates_info):
                    print(f"and the {row[1]['Rate Type']} at {row[1]['Rate (%)']} percent.")
                else:
                    print(f"the {row[1]['Rate Type']} at {row[1]['Rate (%)']} percent,", end=" ")
                counter += 1
            print("This concludes today's market report. See you tomorrow.")
        except:
            print("...")
            print("There was an error procuring the data necessary to produce the rest of the market report. Please try again later.")  

    #CSV Export (Option 4)
    def csv_export(self):
        agg_dfs = self.agg_dfs()
        try:
            agg_dfs.to_csv("csv_files/mkt_data.csv")
            print("Your export was successful")
        except:
            print("Your export was unsuccessful")

    #Excel Export (Option 5)
    def xlsx_export(self):
        pd.read_csv('csv_files/mkt_data.csv').to_excel('sheets/rawdata.xlsx')

    #Clear Stored Files (Option 6)
    def remove_files(self):
        while True:
            user_input = input("Which file would you like removed (.csv/.xlsx/all)? ").lower()
            if user_input != ".csv" and user_input != ".xlsx" and user_input != "all":
                print("Please enter valid file type")
                continue
            if user_input == ".csv":
                try:
                    os.remove("csv_files/mkt_data.csv")
                    print("Your file was successfully removed")
                except:
                    print("The file you are trying to delete does not exist")
            elif user_input == ".xlsx":
                try:
                    os.remove("sheets/rawdata.xlsx")
                    print("Your file was successfully removed")
                except:
                    print("The file you are trying to delete does not exist")
            elif user_input == 'all':
                both_removed = [True, True]
                try:
                    os.remove("csv_files/mkt_data.csv")
                except:
                    print(".csv file does not exist")
                    both_removed[0] = False
                try:
                    os.remove("sheets/rawdata.xlsx")
                except:
                    print(".xlsx file does not exist")
                    both_removed[1] = False
                if both_removed[0] == True and both_removed[1] == True:
                    print("Both files have been successfully removed")
                elif both_removed[0] == True and both_removed[1] == False:
                    print(".csv file has been successfully removed")
                elif both_removed[1] == True and both_removed[0] == False:
                    print(".xlsx file has been successfully removed")
                elif both_removed[0] == False and both_removed[1] == False:
                    print("There are no files to remove")
            break

class Application():
    def __init__(self) -> None:
        self.app_obj = AppFunctions()
        
    #Menu
    def program_run(self):
        message_width = 75
        user_options = {
            "intro": "Welcome to your Market Dashboard",
            "option_1": "Enter 1 to Use the Data Visualizer",
            "option_2": "Enter 2 to Display Data in Terminal",
            "option_3": "Enter 3 to Generate Market Report",
            "option_4": "Enter 4 to Receive Data in CSV File",
            "option_5": "Enter 5 to Receive Data in Excel File",
            "option_6": "Enter 6 to Clear Stored Files",
            "option_7": "Enter 7 to Quit Program"
        }
        error_messages = {
            "non_int": "Please enter a valid option (Error: User input is not number)",
            "out_of_range_int": "Please enter a valid option (Error: User input is not 1-7)"
        }
        while True:
            for key, value in user_options.items():
                fill_len = (message_width-len(value))//2
                if key == 'intro':
                    print(f'{"*"*fill_len} {value} {"*"*fill_len}')
                else:
                    print(f'{" "*fill_len} {value} {" "*fill_len}')
            print("*"*message_width)

            user_input = int(input("Please enter your option: "))
            if user_input > 7 or user_input < 1:
                print(error_messages['out_of_range_int'])
                continue
            #Output Func Calls
            print()
            if user_input == 1:
                self.app_obj.visualizer()
            elif user_input == 2:
                self.app_obj.term_print()
            elif user_input == 3:
                self.app_obj.gen_mkt_report()
            elif user_input == 4:
                self.app_obj.csv_export()
            elif user_input == 5:
                self.app_obj.xlsx_export()
            elif user_input == 6:
                self.app_obj.remove_files()
            elif user_input == 7:
                print("Thank you for using the app, see you tomorrow!")
                break
            print()
        print()

def main():
   print(f"{((75-10)//2) * '*'}Loading...{((75-10)//2) * '*'}", end='\r')
   obj = Application()
   obj.program_run()
main()
