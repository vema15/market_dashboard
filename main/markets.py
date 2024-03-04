import requests as rq
import pandas as pd
import numpy as np
from yahoo_fin import stock_info as si
import os
import matplotlib.pyplot as plt
from datetime import datetime

#MARKET FUNCTIONS

class MktAppFunctions:
    def __init__(self) -> None:
        self.master_frames = [MktAppFunctions.get_ref_rates(), MktAppFunctions.get_repo_rr_ops(), MktAppFunctions.get_equity_inds()]
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

#ECONOMY FUNCTIONS

class EconAppFunctions:
    api_key = "863833a039ac133dca6d4e28e7215ae8"
    base_url_1 = "https://api.stlouisfed.org/fred/series/observations?series_id="
    base_url_2 = f"&api_key={api_key}&sort_order=desc&file_type=json"
    
    def __init__(self) -> None:
        ##US ECON FIGURES##

        #Economic Growth Figures
        self.econ_growth_ids = {
            "real_gdp": ("Real GDP","GDPC1", "Billions of Chained 2017 Dollars ", "Quarterly")
        }

        #Household Income and Expenditures    
        self.house_inc_exp_ids = {
            "pers_savings_rate": ("Personal Savings Rate","PSAVERT", "Percent" , "Monthly"),
            "real_disp_income": ("Real Disposable Income","DSPIC96", "Billions of Chained 2017 Dollars" , "Monthly"),
            "retail_sales": ("Retail Sales","MRTSSM44000USS", "Millions of Dollars" , "Montly"),
            "consumer_credit": ("Consumer Credit","TOTALSL", "Billions of Dollars" , "Monthly"),
            "consumer_credit_del": ("Consumer Credit Delinquency Rate","DRCCLACBS", "Percent" , "Quarterly"),
            "consumer_sentiment": ("Consumer Sentiment (UMich)","UMCSENT", "Index 1966:Q1=100" , "Monthly")
        }
    
        #Business Profits and Investments
        self.bus_prof_inv_ids = {
            "corp_profits_at": ("Corporate Profits after Taxes","CP", "Billions of Dollars", "Quarterly")
        }

        #Labor
        self.labor_ids = {
            "employment_level": ("Employment Level","CE16OV", "Thousands of Persons", "Monthly"),
            "avg_total_priv_hours": ("Average Total Private Work Hours","AWHAETP", "Hours", "Monthly"),
            "avg_total_priv_earnings": ("Average Total Private Work Earnings","CES0500000011", "Dollars per Week", "Monthly"),
            "employment_cost_ind_priv": ("Private Employment Cost Index","ECIWAG", "Index Dec 2005=100", "Quarterly"),
            "job_openings_priv": ("Private Job Openings","JTS1000JOL", "Level in Thousands", "Monthly"),
            "unemployment_rate": ("Unemployment Rate","UNRATE", "Percent", "Monthly"),
            "nonfarm_lab_productivity": ("Non-Farm Labor Productivity","OPHNFB", "Index 2017=100", "Quarterly"),
            "nonfarm_unit_lab_costs": ("Non-Farm Unit Labor Costs","ULCNFB", "Index 2017 = 100", "Quarterly")
        }

        #Inflation and Deflation
        self.inf_def_ids = {
            "med_cpi": ("Median CPI","MEDCPIM158SFRBCLE", "Percent Change at Annual Rate", "Monthly"),
            "ppi_all_commods": ("PPI (All Commodities)","PPIACO", "Index 1982=100", "Monthly"),
            "import_price_ind": ("Import Price Index","IR", "Index 2000 = 100", "Monthly"),
            "export_price_ind": ("Export Price Index","IQ", "Index 2000 = 100", "Monthly")
        }
    
        #Production
        self.production_ids =  {
            "industrial_prod": ("Industrial Production Index","INDPRO", "Index 2017 = 100", "Monthly"),
            "capacity_util_ind": ("Capacity Utilization Index","TCU", "Percent of Capacity", "Monthly"),
            "manu_new_ord": ("Manufacturers New Orders","AMTMNO", "Millions of Dollars", "Monthly"),
            "inv_to_sales": ("Inventory-to-Sales Ratio","ISRATIO", "Ratio", "Monthly")
        }

        #Housing
        self.housing_ids = {
            "house_price_ind": ("Housing Price Index","USSTHPI", "Index 1980:Q1 = 100", "Quarterly"),
            "housing_starts": ("Housing Starts","HOUST", "Thousands of Units", "Monthly"),
            "exis_home_sales": ("Existing Home Sales","EXHOSLUSM495S", "Number of Units", "Monthly"),
            "new_sfr_sales": ("New Single Family Residential Home Sales","HSN1F", "Thousands", "Monthly"),
            "home_vac_rate": ("Home Vacancy Rate","USHVAC", "Percent", "Annual"),
            "house_afford_index": ("Housing Affordability Index","FIXHAI", "Index", "Monthly"),
            "sfr_delinquency": ("Single Family Residential Mortgage Delinquency Rate","DRSFRMACBS", "Percent", "Quarterly"),
        }

        #Finance
        self.finance_ids = {
            "bank_loans": ("Bank Loans","TOTLL", "Billions of U.S. Dollars", "Weekly")
        }

        #Government
        self.gov_ids = {
            "gov_exp": ("Government Expenditures","FGEXPND", "Billions of Dollars", "Quarterly")
        }
  
        #Economic Well-Being
        self.econ_wb_ids = {
            "one_pct_wealth_share": ("Share of Wealth (top 1%)","WFRBST01134", "Percent of Aggregate", "Quarterly"),
            "poverty_pct": ("Poverty Rate","PPAAUS00000A156NCEN", "Percent", "Annual")
        }
    
        ##INTERNATIONAL FIGURES##
        self.intl_figs_ids = {
            "bal_of_trade": ("Balance of Trade","BOPGSTB", "Millions of Dollars", "Monthly"),
            "intl_invest_position": ("International Investment Position","IIPUSNETIQ", "Millions of Dollars", "Quarterly")
        }

    ##DATA AGGREGATION AND MODIFICATION METHODS##
    
    def agg_category(self, category):
        series_data_list = []
        for key, value in category.items():
            total_url = EconAppFunctions.base_url_1+value[1]+EconAppFunctions.base_url_2
            data_req = rq.get(total_url)
            data_req_json = data_req.json()
            series_data_list.append((value[0], value[2], value[3], data_req_json['observations'][0]['date'], data_req_json['observations'][0]['value'], data_req_json['observations'][1]['date'],  data_req_json['observations'][1]['value'], (((float(data_req_json['observations'][0]['value'])-float(data_req_json['observations'][1]['value']))/float(data_req_json['observations'][1]['value'])) * 100)))
        econ_df = pd.DataFrame(series_data_list, columns=['|Indicator|', '|Units|', '|Observation Interval|', '|Latest Observation Date|', '|Latest Observation Value|', '|Penultimate Observation Date|', '|Penultimate Observation Value|', '|Change in Value between Periods (%)|'])
        econ_df.set_index('|Indicator|', inplace=True)
        return econ_df
    
    #Economic Report
    def econ_report(self):
        def exp_cont_inc_dec(series, verbiage):
            tedious_col_name = '|Change in Value between Periods (%)|'
            if verbiage == 'ec':
                if series[tedious_col_name] > 0:
                    return 'expansion'
                elif series[tedious_col_name] < 0:
                    return 'contraction'
                else:
                    return 'stagnation'
            elif verbiage == 'id':
                if series[tedious_col_name] > 0:
                    return 'increase'
                elif series[tedious_col_name] < 0:
                    return 'decrease'
                else:
                    return 'flatline'
        
        def pct_grabber(series):
            tedious_col_name = '|Change in Value between Periods (%)|'
            return f"{series[tedious_col_name]:.2f}%"

        categories_list = [self.econ_growth_ids,self.house_inc_exp_ids,self.bus_prof_inv_ids,self.labor_ids,self.inf_def_ids,self.production_ids,self.housing_ids,self.finance_ids,self.gov_ids,self.econ_wb_ids,self.intl_figs_ids]
        print(f"[{((75-30)//2) * '*'} Loading Economic Report... {((75-30)//2) * '*'}]", end="\r")
        df_agg_cat_list = [self.agg_category(x) for x in categories_list]
        text_list = [
            "***Disclaimer: The following indicators are updated at different intervals, and, for those release at the same interval, release dates may vary. This report serves to give a general economic outlook in a range of three to six months of the U.S. economy. Each indicator's observation interval is depicted by the following:\nw: Weekly\nm: Monthly\nq: Quarterly\na: Annual\n***",
            f"Prepared on {datetime.today()}",
            "\n"
            f"Beginning with economic growth, there has been a {pct_grabber(df_agg_cat_list[0].loc['Real GDP'])} {exp_cont_inc_dec(df_agg_cat_list[0].loc['Real GDP'], 'ec')} in Real GDP (q).",
            f"With regard to the economy's price level, there has been a(n) {pct_grabber(df_agg_cat_list[4].loc['Median CPI'])} {exp_cont_inc_dec(df_agg_cat_list[4].loc['Median CPI'], 'id')} in the Median CPI (m) [**measures YoY change on a monthly basis]. On the producer side, there has been a {pct_grabber(df_agg_cat_list[4].loc['PPI (All Commodities)'])} {exp_cont_inc_dec(df_agg_cat_list[4].loc['PPI (All Commodities'], 'id')} in the prices paid (m) for commodities. For international trade, there has been a {pct_grabber(df_agg_cat_list[4].loc['Import Price Index'])} {exp_cont_inc_dec(df_agg_cat_list[4].loc['Import Price Index'], 'id')} in import prices (m) and a {pct_grabber(df_agg_cat_list[4].loc['Export Price Index'])} {exp_cont_inc_dec(df_agg_cat_list[4].loc['Export Price Index'], 'id')} in export prices (m)."
            f"The U.S. Total Trade Balance (m) and International Investment Position (m) have {exp_cont_inc_dec(df_agg_cat_list[10].loc['Balance of Trade'], 'id')}d by {pct_grabber(df_agg_cat_list[10].loc['Balance of Trade'])} and {exp_cont_inc_dec(df_agg_cat_list[10].loc['International Investment Position'], 'id')}d by {pct_grabber(df_agg_cat_list[10].loc['International Investment Position'])} respectively.",
            f"For U.S. consumers, there has been a(n) {pct_grabber(df_agg_cat_list[1].loc['Personal Savings Rate'])} {exp_cont_inc_dec(df_agg_cat_list[1].loc['Personal Savings Rate'], 'id')} in the Personal Savings Rate (m), which was accompanied by a respective {pct_grabber(df_agg_cat_list[1].loc['Retail Sales'])} {exp_cont_inc_dec(df_agg_cat_list[1].loc['Retail Sales'], 'id')} and {pct_grabber(df_agg_cat_list[1].loc['Consumer Credit'])} {exp_cont_inc_dec(df_agg_cat_list[1].loc['Consumer Credit'], 'id')} in Retail Sales (m) and Consumer Credit Balances (m) ({pct_grabber(df_agg_cat_list[1].loc['Consumer Credit Delinquency Rate'])} {exp_cont_inc_dec(df_agg_cat_list[1].loc['Consumer Credit Delinquency Rate'], 'id')} in Consumer Credit Delinquencies (q)). To finish off with Consumer Sentiment (m), there has been a(n) {exp_cont_inc_dec(df_agg_cat_list[1].loc['Consumer Sentiment (UMich)'], 'id')} in consumer attitudes.",
            f"On the other side of the same coin, U.S. producers have seen an overall {exp_cont_inc_dec(df_agg_cat_list[5].loc['Industrial Production Index'], 'ec')} of Industrial Production (m) ({pct_grabber(df_agg_cat_list[5].loc['Industrial Production Index'])}) with {exp_cont_inc_dec(df_agg_cat_list[5].loc['Capacity Utilization Index'], 'id')}d Capacity Utilization (m) ({pct_grabber(df_agg_cat_list[5].loc['Capacity Utilization Index'])}). On the demand side of the producers, there has been a(n) {exp_cont_inc_dec(df_agg_cat_list[5].loc['Inventory-to-Sales Ratio'], 'id')} of Inventory Turnover (m) by {pct_grabber(df_agg_cat_list[5].loc['Inventory-to-Sales Ratio'])} and a {pct_grabber(df_agg_cat_list[5].loc['Manufacturers New Orders'])} {exp_cont_inc_dec(df_agg_cat_list[5].loc['Manufacturers New Orders'], 'id')} of New Orders (m).",
            f"U.S. corporations have seen a(n) {exp_cont_inc_dec(df_agg_cat_list[2].loc['Corporate Profits after Taxes'], 'id')} in their profits (q) by a margin of {pct_grabber(df_agg_cat_list[2].loc['Corporate Profits after Taxes'])}.",
            f"In the labor market, we have seen a {pct_grabber(df_agg_cat_list[3].loc['Employment Level'])} {exp_cont_inc_dec(df_agg_cat_list[3].loc['Employment Level'], 'ec')} of the employment level (m) and a(n) {exp_cont_inc_dec(df_agg_cat_list[3].loc['Unemployment Rate'], 'id')} in the Unemployment Rate (m) of {pct_grabber(df_agg_cat_list[3].loc['Unemployment Rate'])}. For those in the private sector, private laborers' average weekly hours (m) and their accompanying weekly wages (m) saw a {pct_grabber(df_agg_cat_list[3].loc['Average Total Private Work Hours'])} {exp_cont_inc_dec(df_agg_cat_list[3].loc['Average Total Private Work Hours'], 'id')} and a {pct_grabber(df_agg_cat_list[3].loc['Average Total Private Work Earnings'])} {exp_cont_inc_dec(df_agg_cat_list[3].loc['Average Total Private Work Earnings'], 'id')}. Under such conditions, there has been a {pct_grabber(df_agg_cat_list[3].loc['Non-Farm Labor Productivity'])} {exp_cont_inc_dec(df_agg_cat_list[3].loc['Non-Farm Labor Productivity'], 'id')} in Labor Productivity (q) over the past quarter.\n On the private employer side, the overall cost of employment (q) has had a(n) {exp_cont_inc_dec(df_agg_cat_list[3].loc['Private Employment Cost Index'], 'id')} of {pct_grabber(df_agg_cat_list[3].loc['Private Employment Cost Index'])}, accompanied by a {pct_grabber(df_agg_cat_list[3].loc['Non-Farm Unit Labor Costs'])} {exp_cont_inc_dec(df_agg_cat_list[3].loc['Non-Farm Unit Labor Costs'], 'id')} of Non-Farm Unit Labor Costs (q).",
            f"Housing affordability (m) in the American Real Estate market has {exp_cont_inc_dec(df_agg_cat_list[6].loc['Housing Affordability Index'], 'id')}d by {pct_grabber(df_agg_cat_list[6].loc['Housing Affordability Index'])}, with an accompanying {pct_grabber(df_agg_cat_list[6].loc['Housing Price Index'])} {exp_cont_inc_dec(df_agg_cat_list[6].loc['Housing Price Index'], 'id')} in housing prices (q). On the supply side, new single-family residential property sales (m) saw a(n) {pct_grabber(df_agg_cat_list[6].loc['New Single Family Residential Home Sales'])} {exp_cont_inc_dec(df_agg_cat_list[6].loc['New Single Family Residential Home Sales'], 'id')} and existing residential property sales (m) saw a(n) {pct_grabber(df_agg_cat_list[6].loc['Existing Home Sales'])} {exp_cont_inc_dec(df_agg_cat_list[6].loc['Existing Home Sales'], 'id')}. Housing Starts (m) have {exp_cont_inc_dec(df_agg_cat_list[6].loc['Housing Starts'], 'id')}d by {pct_grabber(df_agg_cat_list[6].loc['Housing Starts'])}. Mortgage Delinquency Rates (q) have had a(n) {pct_grabber(df_agg_cat_list[6].loc['Single Family Residential Mortgage Delinquency Rate'])} {exp_cont_inc_dec(df_agg_cat_list[6].loc['Single Family Residential Mortgage Delinquency Rate'], 'id')}.",
            f"In terms of financing the economy, under the current rate conditions, there has been a {pct_grabber(df_agg_cat_list[7].loc['Bank Loans'])} {exp_cont_inc_dec(df_agg_cat_list[7].loc['Bank Loans'], 'id')} in Bank Loans (w).",
            f"The U.S. Government has seen a {pct_grabber(df_agg_cat_list[8].loc['Government Expenditures'])} {exp_cont_inc_dec(df_agg_cat_list[8].loc['Government Expenditures'], 'id')} in Expenditures (q).",
            f"To finish off with the state of economic wellbeing in the United States, there has been a {pct_grabber(df_agg_cat_list[9].loc['Share of Wealth (top 1%)'])} {exp_cont_inc_dec(df_agg_cat_list[9].loc['Share of Wealth (top 1%)'], 'id')} in the one percent's share of the nation's wealth (q) and a {pct_grabber(df_agg_cat_list[9].loc['Poverty Rate'])} {exp_cont_inc_dec(df_agg_cat_list[9].loc['Poverty Rate'], 'id')} in the poverty rate (a).",
            "Thank you so much for reading, and we'll catch you next time."
        ] 

        for line in text_list:
            print(line)

        print()
        cont_input = input("Please Press Enter to Continue")
        if cont_input:
            return
        
        
#MASTER UI

class UserInterface():
    def __init__(self) -> None:
        self.mkt_app_obj = MktAppFunctions()
        self.econ_app_obj = EconAppFunctions()
        
    #Market Menu
    def mkt_ui_run(self):
        message_width = 75
        user_options = {
            "intro": "Welcome to the Market Dashboard",
            "option_1": "Enter 1 to Use the Data Visualizer",
            "option_2": "Enter 2 to Display Data in Terminal",
            "option_3": "Enter 3 to Generate Market Report",
            "option_4": "Enter 4 to Receive Data in CSV File",
            "option_5": "Enter 5 to Receive Data in Excel File",
            "option_6": "Enter 6 to Clear Stored Files",
            "option_7": "Enter 7 to Return to Main Menu"
        }
        error_messages = {
            "non_int": "Please enter a valid option (Error: User input is not number)",
            "out_of_range_int": "Please enter a valid option (Error: User input is not 1-7)"
        }
        while True:
            print("*" * (message_width))
            for key, value in user_options.items():
                wt_space_amt = (((message_width - len(value))-2)//2)
                if wt_space_amt % 2 == 0:
                    print(f"*{' ' * ((((message_width - len(value))-2)//2))}{value}{' ' * ((((message_width - len(value))-1)//2))}*")
                else:
                    print(f"*{' ' * ((((message_width - len(value))-2)//2))}{value}{' ' * ((((message_width - len(value))-1)//2))}*")
            print("*" * (message_width))
            print()
            try:
                user_input = int(input("Please enter your option: "))
                if user_input > 7 or user_input < 1:
                    print(error_messages['out_of_range_int'])
                    continue
                #Output Func Calls
                print()
                if user_input == 1:
                    self.mkt_app_obj.visualizer()
                elif user_input == 2:
                    self.mkt_app_obj.term_print()
                elif user_input == 3:
                    self.mkt_app_obj.gen_mkt_report()
                elif user_input == 4:
                    self.mkt_app_obj.csv_export()
                elif user_input == 5:
                    self.mkt_app_obj.xlsx_export()
                elif user_input == 6:
                    self.mkt_app_obj.remove_files()
                elif user_input == 7:
                    break
                print()
            except:
                print(error_messages['non_int'])
            user_input = input("Press Enter to Continue")
            if user_input:
                continue
        print()
    
    def econ_series_menu(self):
        message_width = 75
        user_options = {
            "intro": "Economic Categories Menu",
            "option_1": "Enter 1 for Economic Growth Figures",
            "option_2": "Enter 2 for Household Income and Expenditures Figures",
            "option_3": "Enter 3 for Business Profits and Investments Figures",
            "option_4": "Enter 4 for Labor Figures",
            "option_5": "Enter 5 for Inflation and Deflation Figures",
            "option_6": "Enter 6 for Production Figures",
            "option_7": "Enter 7 for Housing Figures",
            "option_8": "Enter 8 for Finance Figures",
            "option_9": "Enter 9 for Government Figures",
            "option_10": "Enter 10 for Economic Well-Being Figures",
            "option_11": "Enter 11 for International Trade Figures",
            "option_12": "Enter 12 to Return to the Main Economic Menu"
        }

        error_messages = {
            "non_int": "Please enter a valid option (Error: User input is not number)",
            "out_of_range_int": "Please enter a valid option (Error: User input is not 1-12)"
        }
        while True:
            print("x" * (message_width))
            for key, value in user_options.items():
                wt_space_amt = (((message_width - len(value))-2)//2)
                if wt_space_amt % 2 == 0:
                    print(f"x{' ' * ((((message_width - len(value))-2)//2))}{value}{' ' * ((((message_width - len(value))-1)//2))}x")
                else:
                    print(f"x{' ' * ((((message_width - len(value))-2)//2))}{value}{' ' * ((((message_width - len(value))-1)//2))}x")
            print("x" * (message_width))
            print()
            try:
                user_input = int(input("Please enter your option: "))
                if user_input > 12 or user_input < 1:
                    print(error_messages["out_of_range_int"])
                    continue
                print()
                if user_input == 1:
                    category = self.econ_app_obj.econ_growth_ids
                elif user_input == 2:
                    category = self.econ_app_obj.house_inc_exp_ids
                elif user_input == 3:
                    category = self.econ_app_obj.bus_prof_inv_ids
                elif user_input == 4:
                    category = self.econ_app_obj.labor_ids
                elif user_input == 5:
                    category = self.econ_app_obj.inf_def_ids
                elif user_input == 6:
                    category = self.econ_app_obj.production_ids
                elif user_input == 7:
                    category = self.econ_app_obj.housing_ids
                elif user_input == 8:
                    category = self.econ_app_obj.finance_ids
                elif user_input == 9:
                    category = self.econ_app_obj.gov_ids
                elif user_input == 10:
                    category = self.econ_app_obj.econ_wb_ids
                elif user_input == 11:
                    category = self.econ_app_obj.intl_figs_ids
                elif user_input == 12:
                    return
                print(f"[{((75-14)//2) * '*'} Loading... {((75-14)//2) * '*'}]", end="\r", flush=True)
                print(self.econ_app_obj.agg_category(category))
                print()
            except:
                print(error_messages['non_int'])
            user_input = input("Press Enter to Continue")
            if user_input:
                continue
            print()

    #Economy Menu
    def econ_ui_run(self):
        message_width = 75
        user_options = {
            "intro": "Welcome to the Economic Dashboard",
            "option_1": "Enter 1 to View Categorical Series Menu",
            "option_2": "Enter 2 to View the Economic Report",
            "option_3": "Enter 3 to Return to Main Menu"
        }
        error_messages = {
            "non_int": "Please enter a valid option (Error: User input is not number)",
            "out_of_range_int": "Please enter a valid option (Error: User input is not 1-3)"
        }

        while True:
            print("*" * (message_width))
            for key, value in user_options.items():
                wt_space_amt = (((message_width - len(value))-2)//2)
                if wt_space_amt % 2 == 0:
                    print(f"*{' ' * ((((message_width - len(value))-2)//2))}{value}{' ' * ((((message_width - len(value))-1)//2))}*")
                else:
                    print(f"*{' ' * ((((message_width - len(value))-2)//2))}{value}{' ' * ((((message_width - len(value))-1)//2))}*")
            print("*" * (message_width))
            print()
            try:
                user_input = int(input("Please enter your option: "))
                if user_input > 3 or user_input < 1:
                    print(error_messages['out_of_range_int'])
                    continue
                #Output Func Calls
                print()
                if user_input == 1:
                    self.econ_series_menu()
                elif user_input == 2:
                    self.econ_app_obj.econ_report()
                elif user_input == 3:
                    break
            except:
                print(error_messages['non_int'])
            print()

#TOP-LEVEL APPLICATION

class Application:
    def __init__(self) -> None:
        pass

    def menu_select(self):
        message_width = 75
        print(f"[{((75-14)//2) * '*'} Loading... {((75-14)//2) * '*'}]", end='\r')   
        ui_obj = UserInterface()
        ui_msgs = {
            'welcome_message': "Welcome to the One Stop Shop for Markets and Economic Data!",
            'input_message': 'Please Enter Your Desired Data Field (Economy/Markets):'
        }
        user_options = {
            "option_1": "Enter 1 to View Market Dashboard",
            "option_2": "Enter 2 to View Economic Data Menu",
            "option_3": "Enter 3 to Quit Program"
        }
        print(f"{' ' * ((message_width-len(ui_msgs['welcome_message']))//2)}{ui_msgs['welcome_message']}{' ' * ((message_width-len(ui_msgs['welcome_message']))//2)}")
        while True:
            print("|" * (message_width))
            for key, value in user_options.items():
                wt_space_amt = (((message_width - len(value))-2)//2)
                if wt_space_amt % 2 == 0:
                    print(f"|{' ' * ((((message_width - len(value))-2)//2))}{value}{' ' * ((((message_width - len(value))-1)//2))}|")
                else:
                    print(f"|{' ' * ((((message_width - len(value))-2)//2))}{value}{' ' * ((((message_width - len(value))-1)//2))}|")
            print("|" * (message_width))
            print()
            try:
                menu_select = int(input("Please Enter Your Option: "))
            except:
                print("Please Enter a Valid Option (error: non-integer)")
                continue
            if menu_select > 3 or menu_select < 1:
                print("Please Enter a Valid Number (1-3)")
                continue
            print()
            if menu_select == 1:
                ui_obj.mkt_ui_run()
            elif menu_select == 2:
                ui_obj.econ_ui_run()
            elif menu_select == 3:
                print("See You Tomorrow!")
                break
            print()

def main():
   app_obj = Application()
   app_obj.menu_select()
 
main()
