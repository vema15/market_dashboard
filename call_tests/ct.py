import requests as rq
import pandas as pd
from openpyxl import load_workbook
from yahoo_fin import stock_info as si
import os


#FED Market Data API
base_url = "https://markets.newyorkfed.org"
ltw = "/api/rp/all/all/results/lastTwoWeeks.json"

repo_rate_url = base_url+ltw
repo_rate_response = rq.get(repo_rate_url)
repo_rate_json = repo_rate_response.json()

#FRED API
api_key = '863833a039ac133dca6d4e28e7215ae8'
base_url_2 = "https://api.stlouisfed.org/fred/"
releases = f"releases?api_key={api_key}&file_type=json"
real_gdp = f"series/observations?series_id=GDPC1&api_key={api_key}&sort_order=desc&file_type=json"
total_url = base_url_2+real_gdp

econ_data_resp = rq.get(total_url)
print(econ_data_resp.json())