#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 11:30:49 2021

@author: Sarah
"""
import pandas as pd
import pandasql
import dash
from dash.dependencies import Input, Output
# import dash_core_components as dcc #this had to be changed
from dash import dcc
# import dash_html_components as html #this as well
from dash import html
import plotly.express as px
from urllib.request import urlopen
import json

pd.options.mode.chained_assignment = None  # default='warn'
px.set_mapbox_access_token(open("mapbox_token.txt").read())

# get vaccination data from rki vaccination github repo:
# (https://github.com/robert-koch-institut/COVID-19-Impfungen_in_Deutschland)
url_vacc_data = "https://raw.githubusercontent.com/robert-koch-institut/COVID-19-Impfungen_in_Deutschland/master/Aktuell_Deutschland_Impfquoten_COVID-19.csv"
# read-in data from csv-file (filter out Deutschland & Bundesressorts)
vacc_data = pd.read_csv(url_vacc_data, skiprows=[1, 18])

## Read-in Vacc-History
with urlopen("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv") as vacc_his:
    vacc_history = pd.read_csv(vacc_his)

vacc_history = vacc_history[vacc_history.location == "Germany"]
#print(vacc_history.to_string())
fully_vacc_germany = vacc_history[["date", "people_fully_vaccinated_per_hundred"]]
fully_vacc_germany = fully_vacc_germany[fully_vacc_germany.date >= "2021-06-07"]

# Open Germany map as GeoJSON
with urlopen("https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json") as file:
    germany_states = json.load(file)

# Read-in Covid-Data (States)
with urlopen("https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/Coronaf%C3%A4lle_in_den_Bundesl%C3%A4ndern/FeatureServer/0/query?where=1%3D1&outFields=LAN_ew_AGS,LAN_ew_GEN,Aktualisierung,cases7_bl_per_100k,death7_bl,cases7_bl_per_100k_txt,cases7_bl&outSR=4326&f=json") as cases_states:
    covid_states = json.load(cases_states)

covid_data = pd.json_normalize(covid_states, record_path=['features'])

## Read-in historical Case-Data
with urlopen("https://raw.githubusercontent.com/jgehrcke/covid-19-germany-gae/master/cases-rki-by-state.csv") as cov_history:
    covid_history = pd.read_csv(cov_history)

covid_history_germany = covid_history[["time_iso8601", "sum_cases"]]
covid_history_germany.sum_cases = covid_history_germany.sum_cases.astype(int)
covid_history_june = covid_history_germany[covid_history_germany["time_iso8601"] > "2021-06-06T17:00:00+0000"]
covid_daily_cases_june = covid_history_june[["time_iso8601", "sum_cases"]]
covid_daily_cases_june["daily_cases"] = covid_daily_cases_june.sum_cases.diff().fillna(1686).astype(int)


## Read in Voting-Results
with urlopen("https://raw.githubusercontent.com/julianrosenberger/VisualizationSDU/main/data/kerg2.csv?token=ARUOLO6FZZDDUIENM6H2R6DBYOBVQ") as f:
    data = pd.read_csv(f, delimiter=';', skiprows=9, usecols=['Gebietsnummer', 'Gebietsname', 'UegGebietsnummer', 'Gruppenart', 'Gruppenname', 'Gruppenreihenfolge', 'Stimme',	'Prozent'])


# #Deleting where Gruppenart!=Partei
df_clear=data[data.Gruppenart=="Partei"]

# deleting Stimme==2:
df_clear2 = df_clear[df_clear.Stimme==1]

# Grouped dataframe with only the states 1-16 (both incl.)
df_clear3 = df_clear2[df_clear2.Gebietsnummer < 17]

# Make sure Gebietsnummer belongs to state
df_clear4 = df_clear3[df_clear3.UegGebietsnummer == 99]


df_clear = df_clear4

# cleaning 
#print(type('Prozent')) # string --> convert to int

#(nan --> 0
df_clear['Prozent'] = df_clear['Prozent'].fillna(0)

# , --> .
df_clear['Prozent'] = (df_clear['Prozent'].replace(',', '.', regex=True).astype(float))

# string --> int
df_clear['Prozent'] = pd.to_numeric(df_clear['Prozent'])

#print(df_clear.to_string())


# Gruping by state:
df_group = df_clear.groupby('Gebietsnummer')
#print(df_group)
#print(df_group['Gebietsnummer'] == 11)

# for key, item in df_group:
#     print(df_group.get_group(key))

# Get the indices of the original dataframe to find out which party etc. it belongs to:
#idx = df_group(['Gebietsnummer'])['Prozent'].transform(max) == df_clear['Prozent']
#print(idx.head())

maximums = df_group['Prozent'].max()
#print(maximums.to_string())

#print(df_clear.loc[df_clear.groupby(['Gebietsnummer'])['Prozent'].idxmax()].reset_index(drop=True))

winners = df_clear.loc[df_clear.groupby(['Gebietsnummer'])['Prozent'].idxmax()].reset_index(drop=True)
#print(winners.to_string())










#parties = ["SPD", "GRÜNE", "CDU", "AfD"]

#voting_results = pd.DataFrame(columns=['StateID', 'State', 'Party', 'Result'])
#winners = pd.DataFrame(columns=['State', 'Party', 'Result'])




#for i in range(len(data)):
#    for state_id in range(1, 17):
#        for party in parties:
#            if state_id == 9:
#                parties[2] = "CSU"
#            else:
#                parties[2] = "CDU"
#
#            if data.loc[i, 'Gebietsnummer'] == state_id and data.loc[i, 'Gruppenname'] == party and data.loc[i, 'Stimme'] == 1:
#                voting_results = voting_results.append({'StateID': data.loc[i, 'Gebietsnummer'],
#                                                        'State': data.loc[i, 'Gebietsname'],
#                                                        'Party': data.loc[i, 'Gruppenname'],
#                                                        'Result': data.loc[i, 'Prozent']},
#                                                       ignore_index=True)
#
#                winners = pandasql.sqldf("SELECT State, Party, MAX(Result) FROM voting_results GROUP BY StateID")

# for j in range(len(voting_results)):
#     for state_id in range (1, 17):
#         # max_value = voting_results[j, 'Result']
#         if voting_results[j, 'Gebietsnummer'] == voting_results[j + 1, 'Gebietsnummer']:
#
#
#         if voting_results[j, 'Result'] > max_value:
#             max_value = voting_results[j, 'Result']
#
#         winners = winners.append({'State': , 'Party': , 'Result': }, ignore_index=True)


## Plot Vaccination Map
vacc = px.choropleth_mapbox(
                    mapbox_style='dark',
                    data_frame=vacc_data,
                    geojson=germany_states,
                    locations='Bundesland',
                    featureidkey='properties.name',
                    hover_name='Bundesland',
                    hover_data={'Bundesland': False,
                                'Impfquote_gesamt_voll': ':.2f%',
                                'Datum': True},
                    color='Impfquote_gesamt_voll',
                    color_continuous_scale=px.colors.sequential.Blues,
                    labels={'Impfquote_gesamt_voll': 'Fully vaccinated', 'Bundesland': 'State', 'Datum': 'Date'}
                    )
vacc.update_mapboxes(
    center_lat=51.5,
    center_lon=10.25,
    zoom=4.6
)
vacc.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        plot_bgcolor="#2E313B",
        paper_bgcolor="#2E313B",
        font={"color": "#ffffff"}
)

vaccination_history = px.line(
    fully_vacc_germany,
    x='date',
    y='people_fully_vaccinated_per_hundred'
)
vaccination_history.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        plot_bgcolor="#2E313B",
        paper_bgcolor="#2E313B",
        font={"color": "#ffffff"},
        font_color="white",
        yaxis_range=[20, 100]
)

## Plot Covid-Map
cov = px.choropleth_mapbox(
    mapbox_style='dark',
    data_frame=covid_data,
    geojson=germany_states,
    locations='attributes.LAN_ew_GEN',
    featureidkey='properties.name',
    hover_name='attributes.LAN_ew_GEN',
    hover_data={'attributes.LAN_ew_GEN': False,
                'attributes.cases7_bl_per_100k': ':.2f',
                'attributes.death7_bl': True},
    color='attributes.cases7_bl_per_100k',
    color_continuous_scale=px.colors.sequential.YlOrRd,
    labels={'attributes.cases7_bl_per_100k': '7-day incidence', 'attributes.LAN_ew_GEN': 'State', 'attributes.death7_bl': '7-day deaths'}
)
cov.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        plot_bgcolor="#2E313B",
        paper_bgcolor="#2E313B",
        font={"color": "#ffffff"}
)
cov.update_mapboxes(
    center_lat=51.5,
    center_lon=10.25,
    zoom=4.6
)

## Plot Voting-results
vote = px.choropleth_mapbox(
    mapbox_style='dark',
    data_frame=winners,
    geojson=germany_states,
    locations='Gebietsname',
    featureidkey='properties.name',
    hover_name='Gebietsname',
    hover_data={'Gebietsname': False,
                'Gruppenname': True,
                'Prozent': ':.2f%'},
    color='Gruppenname',
    color_discrete_map={'SPD': "#E3000F",
                        "CDU": "#1F1E1D",
                        "CSU": "#1F1E1D",
                        "AfD": "#009ee0"},
    labels={'Gebietsname': 'State', 'Gruppenname': 'Party', 'Prozent': 'Result'},
)
vote.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        plot_bgcolor="#2E313B",
        paper_bgcolor="#2E313B",
        legend={
            "font": {"color": "black"},
            "bgcolor": "LightSteelBlue"
        }
)
vote.update_mapboxes(
    center_lat=51.5,
    center_lon=10.25,
    zoom=4.6
)

## Bar Chart for historical data
cov_history = px.bar(
    covid_daily_cases_june,
    x='time_iso8601',
    y='daily_cases',
    labels={'time_iso8601': 'Date', 'daily_cases': 'Daily Cases'}
)
cov_history.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0},
        plot_bgcolor="#2E313B",
        paper_bgcolor="#2E313B",
        font={"color": "#ffffff"},
        font_color="white"
)

# ## Plot Voting-results in form of pie chart:
# # want for entire Germany, instead of states:
# vote_germ = data[data.Gebietsnummer == 99]
# vote_germ = vote_germ[vote_germ.Stimme == 1]
# vote_germ = vote_germ[vote_germ.Gruppenart == "Partei"]
# vote_germ = vote_germ[vote_germ.Gebietsname == "Bundesgebiet"]
#
# # cleaning
# # (nan --> 0
# vote_germ['Prozent'] = vote_germ['Prozent'].fillna(0)
#
# # , --> .
# vote_germ['Prozent'] = (vote_germ['Prozent'].replace(',', '.', regex=True).astype(float))
#
# # string --> int
# vote_germ['Prozent'] = pd.to_numeric(vote_germ['Prozent'])
#
# # print(vote_germ.to_string())


# 47 different states. Diving into: SPD, CDU/CSU, AfD, and "Others":
#vote_germ.loc[vote_germ['Gruppenname'] == "CDU", 'Gruppenname'] = "CDU/CSU"
#vote_germ.loc[vote_germ['Gruppenname'] == "CSU", 'Gruppenname'] = "CDU/CSU"

# vote_germ.loc[vote_germ['Prozent'] < 6, 'Gruppenname'] = "Other"
# vote_germ.loc[vote_germ['Gruppenname'] == "FDP", 'Gruppenname'] = "Other"
# vote_germ.loc[vote_germ['Gruppenname'] == "GRÜNE", 'Gruppenname'] = "Other"

votes = {"Party": ["SPD", "CDU/CSU", "AfD", "Other"], "Result": [25.70, 24.10, 10.30, 39.90]}
vote_germ = pd.DataFrame(votes)

vote_chart = px.pie(vote_germ,
                    values='Result',
                    names='Party',
                    color='Party',
                    color_discrete_map={'SPD': '#E3000F',
                                        'CDU/CSU': '#1F1E1D',
                                        'AfD': '009ee0',
                                        'Other': 'grey'}
)
vote_chart.update_layout(
        #margin={"r": 0, "t": 0, "l": 0, "b": 0},
        plot_bgcolor="#2E313B",
        paper_bgcolor="#2E313B",
        legend={
            "font": {"color": "black"},
            "bgcolor": "LightSteelBlue"
        }
)



## Build web app with dash
app = dash.Dash(__name__)

app.layout = lambda: html.Div(children=[
    # H1-Header
    html.H1(children="Does voting against vaccinations mean voting for COVID?",
            style={'textAlign': 'center', 'fontFamily': 'Helvetica, Arial, sans-serif'}),
    html.Div([
        html.Div([
            dcc.Graph(figure=vacc)
        ], style={'width': '33%', 'float': 'left', 'background-color': '#2E313B'}),
        html.Div([
            dcc.Graph(figure=cov)
        ], style={'width': '33%', 'float': 'left', 'background-color': '#2E313B'}),
        html.Div([
            dcc.Graph(figure=vote)
        ], style={'width': '33%', 'float': 'left', 'background-color': '#2E313B'})
    ]),
    html.Div([
        html.Div([
            dcc.Graph(figure=vaccination_history)
        ], style={'width': '33%', 'float': 'left', 'background-color': '#2E313B'}),
        html.Div([
            dcc.Graph(figure=cov_history)
        ], style={'width': '33%', 'float': 'left', 'background-color': '#2E313B'}),
        html.Div([
            dcc.Graph(figure=vote_chart)
        ], style={'width': '33%', 'float': 'left', 'background-color': '#2E313B'})
    ])
])


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)