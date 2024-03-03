import requests as rq
import pandas as pd
from openpyxl import load_workbook
from yahoo_fin import stock_info as si
import datetime as datetime
import os


##FED Market Data API
#base_url = "https://markets.newyorkfed.org"
#ltw = "/api/rp/all/all/results/lastTwoWeeks.json"
#
#repo_rate_url = base_url+ltw
#repo_rate_response = rq.get(repo_rate_url)
#repo_rate_json = repo_rate_response.json()
#
##FRED API
#api_key = '863833a039ac133dca6d4e28e7215ae8'
#base_url_2 = "https://api.stlouisfed.org/fred/"
#releases = f"releases?api_key={api_key}&file_type=json"
#real_gdp = f"series/observations?series_id=USSTHPI&api_key={api_key}&sort_order=desc&file_type=json"
#
#b1 = "https://api.stlouisfed.org/fred/series/observations?series_id="
#
#b2 = f"&api_key={api_key}&sort_order=desc&file_type=json"
#
#
#econ_data_resp = rq.get(total_url)
#json = econ_data_resp.json()
#


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
            series_data_list.append((value[0], value[2], value[3], data_req_json['observations'][0]['date'], data_req_json['observations'][0]['value'], data_req_json['observations'][1]['date'],  data_req_json['observations'][1]['value'], f"{(((float(data_req_json['observations'][0]['value'])-float(data_req_json['observations'][1]['value']))/float(data_req_json['observations'][1]['value'])) * 100):.2f}%"))
        econ_df = pd.DataFrame(series_data_list, columns=['|Indicator|', '|Units|', '|Release Interval|', '|Latest Release Date|', '|Latest Release Value|', '|Penultimate Release Date|', '|Penultimate Release Value|', '|Percent Change between Periods|'])
        econ_df.set_index('|Indicator|', inplace=True)
        return econ_df
    
    #Economic Report
    def econ_report(self):
       def exp_cont_inc_dec(series, verbiage):
           tedious_col_name = '|Change in Value between Periods (%)|'
           if verbiage == 'ec':
               if series[tedious_col_name] > 0:
                   return 'expansion'
               else:
                   return 'contraction'
           elif verbiage == 'id':
               if series[tedious_col_name] > 0:
                   return 'increase'
               else:
                   return 'decrease'
       
       def pct_grabber(series):
           tedious_col_name = '|Change in Value between Periods (%)|'
           return f"{series[tedious_col_name]:.2f}%"
       categories_list = [self.econ_growth_ids,self.house_inc_exp_ids,self.bus_prof_inv_ids,self.labor_ids,self.inf_def_ids,self.production_ids,self.housing_ids,self.finance_ids,self.gov_ids,self.econ_wb_ids,self.intl_figs_ids]
       print(f"{((75-26)//2) * '*'}Loading Economic Report...{((75-26)//2) * '*'}", end="\r")
       df_agg_cat_list = [self.agg_category(x) for x in categories_list]
       text_list = [
           "***Disclaimer: The following indicators are updated at different intervals, and, for those release at the same interval, release dates may vary. This report serves to give a general economic outlook in a range of three to six months of the U.S. economy. If you would like specific dates for the indicators used, please view the appendix.***",
           "\n",
           #f"Prepared on {datetime.today()}"
           "\n",
           f"Beginning with economic growth, there has been a {pct_grabber(df_agg_cat_list[0].loc['Real GDP'])} {exp_cont_inc_dec(df_agg_cat_list[0].loc['Real GDP'], 'ec')} in Real GDP over the last recorded quarter.",
           "\n",
           #f"The U.S. Total Trade Balance and International Investment Position have {exp_cont_inc_dec(df_agg_cat_list[7].loc['Balance of Trade'], 'id')}d by {pct_grabber(df_agg_cat_list[7].loc['Balance of Trade'])} over the last recorded month and {exp_cont_inc_dec(df_agg_cat_list[7].loc['International Investment Position'], 'id')}d by {pct_grabber(df_agg_cat_list[7].loc['International Investment Position'])} over the last quarter respectively."
       ] 
       for line in text_list:
           print(line)
       print()
       cont_input = input("Please Press Enter to Continue")
       if cont_input:
           return
       

app_obj = EconAppFunctions()
app_obj.econ_report()