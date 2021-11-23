import pandas as pd
import dash
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import plotly.express as px

app = dash.Dash(__name__)

# get vaccination rate from rki vaccination github repo:
# (https://github.com/robert-koch-institut/COVID-19-Impfungen_in_Deutschland)
url_vacc_data = "https://raw.githubusercontent.com/robert-koch-institut/COVID-19-Impfungen_in_Deutschland/master/Aktuell_Deutschland_Impfquoten_COVID-19.csv"
# read-in data from csv-file (skip: Deutschland & Bundesressorts)
vacc_data = pd.read_csv(url_vacc_data, index_col=1, skiprows=[1, 18])
print(vacc_data.head)

print(dir(vacc_data))



minvalue = float()


