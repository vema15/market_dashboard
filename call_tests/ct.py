import requests as rq
import pandas as pd
from openpyxl import load_workbook
from yahoo_fin import stock_info as si
import os

base_url = "https://markets.newyorkfed.org"
ltw = "/api/rp/all/all/results/lastTwoWeeks.json"

repo_rate_url = base_url+ltw
repo_rate_response = rq.get(repo_rate_url)
repo_rate_json = repo_rate_response.json()
