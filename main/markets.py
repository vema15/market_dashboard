import requests as rq
import pandas as pd
from datetime import date
from openpyxl import load_workbook
from yahoo_fin import stock_info as si
import os

#MASTER FUNCTIONS
class AppFunctions:
    def __init__(self) -> None:
        self.master_frames = [AppFunctions.get_ref_rates(), AppFunctions.get_repo_rr_ops(), AppFunctions.get_equity_inds()]
    #**RAW DATAFRAMES**

    #Important Ref Rates Info
    def get_ref_rates():
        rates_url = "https://markets.newyorkfed.org//api/rates/all/latest.json"
        rates_response = rq.get(rates_url)
        rates_json = rates_response.json()
        rates_df = pd.DataFrame(rates_json['refRates'])[['effectiveDate', 'type', 'percentRate']]
        rates_df = rates_df.rename(columns={'effectiveDate': 'Date', 'type': 'Rate Type', 'percentRate': 'Rate (%)'})
        select_rates_df = rates_df.iloc[1:,:]
        return select_rates_df

    #Repo / Reverse Repo Ops
    def get_repo_rr_ops():
        repo_rate_url = "https://markets.newyorkfed.org//api/rp/all/all/results/latest.json"
        repo_rate_response = rq.get(repo_rate_url)
        repo_rate_json = repo_rate_response.json()
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
        return agg_rr_r_df

    #Equity Indices
    def get_equity_inds():
        tickers = [('IVV', 'S&P 500 (ETF)'), 
                   ('QQQ', 'NASDAQ 100 (ETF)'), 
                   ('DIA', 'DJIA (ETF)')]
        index_dfs = []
        for ticker in tickers:
            ind_df = si.get_data(ticker[0]).iloc[-1, :]
            ind_df['Date'] = ind_df.name
            ind_df.name = ticker[1]
            ind_df.drop(columns='adjclose', inplace=True)
            ind_df.rename({'open': 'Open', 'high': 'High', 'low':'Low', 'close': 'Close', 'volume':'Volume', 'ticker': 'Ticker'}, inplace=True)
            index_dfs.append(pd.DataFrame(ind_df).T)
        total_ind_dfs = pd.concat(index_dfs)
        return total_ind_dfs

    #**SYNTHESIZED DATAFRAMES**
    #Get frames
    def agg_dfs(self):
        return pd.concat(self.master_frames)
    
    #**DATA OUTPUT**
    #Excel Export (Option 1)
    def xslx_export(self):
       pass

    #Terminal Print (Option 2)
    def term_print(self):
        for frame in self.master_frames:
            print(frame)

    #CSV Export (Option 3)
    def csv_export(self):
        agg_dfs = self.agg_dfs()
        try:
            agg_dfs.to_csv("csv_files/mkt_data.csv")
            print("Your export was successful")
        except:
            print("Your export was unsuccessful")

    #Clear Stored Files (Option 4)
    def remove_files(self):
        while True:
            user_input = input("Which file would you like removed (.csv/.xlsx)? ").lower()
            if user_input != ".csv" and user_input != ".xlsx":
                print("Please enter valid file type")
                continue
            if user_input == ".csv":
                try:
                    os.remove("csv_files/mkt_data.csv")
                except:
                    print("The file you are trying to delete does not exist")
            elif user_input == ".xlsx":
                try:
                    os.remove("sheets/raw_market_data.xlsx")
                except:
                    print("The file you are trying to delete does not exist")
            print("Your file was successfully removed")
            break

class Application():
    def __init__(self) -> None:
        self.app_obj = AppFunctions()
        
    #Menu
    def program_run(self):
        message_width = 75
        user_options = {
            "intro": "Welcome to your Market Dashboard",
            "option_1": "Enter 1 to Receive Data in Excel File",
            "option_2": "Enter 2 to Display Data in Terminal",
            "option_3": "Enter 3 to Receive Data in CSV File",
            "option_4": "Enter 4 to Clear Stored Files",
            "option_5": "Enter 5 to Quit Program"
        }
        error_messages = {
            "non_int": "Please enter a valid option (Error: User input is not number)",
            "out_of_range_int": "Please enter a valid option (Error: User input is not 1-5)"
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
            if user_input > 5 or user_input < 1:
                print(error_messages['out_of_range_int'])
                continue
            #Output Func Calls
            print()
            if user_input == 1:
                self.app_obj.xslx_export()
            elif user_input == 2:
                self.app_obj.term_print()
            elif user_input == 3:
                self.app_obj.csv_export()
            elif user_input == 4:
                self.app_obj.remove_files()
            elif user_input == 5:
                print("Thank you for using the app, see you tomorrow!")
                break
            print()
        print()

def main():
    print(f"{((75-10)//2) * '*'}Loading...{((75-10)//2) * '*'}", end='\r')
    obj = Application()
    obj.program_run()

main()
