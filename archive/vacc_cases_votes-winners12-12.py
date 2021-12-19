#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Dec 12 11:52:04 2021

@author: Sarah
"""
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
import dash_core_components as dcc #this had to be changed
#from dash import dcc
import dash_html_components as html #this as well
#from dash import html
import plotly.express as px
from urllib.request import urlopen
import json

pd.options.mode.chained_assignment = None  # default='warn'

# get vaccination data from rki vaccination github repo:
# (https://github.com/robert-koch-institut/COVID-19-Impfungen_in_Deutschland)
url_vacc_data = "https://raw.githubusercontent.com/robert-koch-institut/COVID-19-Impfungen_in_Deutschland/master/Aktuell_Deutschland_Impfquoten_COVID-19.csv"
# read-in data from csv-file (filter out Deutschland & Bundesressorts)
vacc_data = pd.read_csv(url_vacc_data, skiprows=[1, 18])

# Open Germany map as GeoJSON
with urlopen("https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json") as file:
    germany_states = json.load(file)

# Read-in Covid-Data (States)
with urlopen("https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/Coronaf%C3%A4lle_in_den_Bundesl%C3%A4ndern/FeatureServer/0/query?where=1%3D1&outFields=LAN_ew_AGS,LAN_ew_GEN,Aktualisierung,cases7_bl_per_100k,death7_bl,cases7_bl_per_100k_txt,cases7_bl&outSR=4326&f=json") as cases_states:
    covid_states = json.load(cases_states)

covid_data = pd.json_normalize(covid_states, record_path=['features'])

## Read in Voting-Results
with urlopen("https://raw.githubusercontent.com/julianrosenberger/VisualizationSDU/main/data/kerg2.csv?token=AQYCHUSY2GHUHR23UV3RZU3BYGNO2") as f:
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
print(type('Prozent')) # string --> convert to int

#(nan --> 0
df_clear['Prozent'] = df_clear['Prozent'].fillna(0)

# , --> .
df_clear['Prozent'] = (df_clear['Prozent'].replace(',', '.', regex=True).astype(float))

# string --> int
df_clear['Prozent'] = pd.to_numeric(df_clear['Prozent'])

#print(df_clear.to_string())


# Gruping by state:
df_group = df_clear.groupby('Gebietsnummer')
print(df_group)
#print(df_group['Gebietsnummer'] == 11)

for key, item in df_group:
    print(df_group.get_group(key))

# Get the indices of the original dataframe to find out which party etc. it belongs to:
#idx = df_group(['Gebietsnummer'])['Prozent'].transform(max) == df_clear['Prozent']
#print(idx.head())

maximums = df_group['Prozent'].max()
#print(maximums.to_string())

#print(df_clear.loc[df_clear.groupby(['Gebietsnummer'])['Prozent'].idxmax()].reset_index(drop=True))

winners = df_clear.loc[df_clear.groupby(['Gebietsnummer'])['Prozent'].idxmax()].reset_index(drop=True)
print(winners.to_string())










## Plot Vaccination Map
vacc = px.choropleth_mapbox(
                    mapbox_style='white-bg',
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
        margin={"r": 0, "t": 0, "l": 0, "b": 0})

## Plot Covid-Map
cov = px.choropleth_mapbox(
    mapbox_style='white-bg',
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
        margin={"r": 0, "t": 0, "l": 0, "b": 0})
cov.update_mapboxes(
    center_lat=51.5,
    center_lon=10.25,
    zoom=4.6
)


## Plot Voting-results
vote = px.choropleth_mapbox(
    mapbox_style='white-bg',
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
                        "CDU": "#32302e",
                        "CSU": "#32302e",
                        "AfD": "#009ee0"},
    labels={'Gebietsname': 'State', 'Gruppenname': 'Party', 'Prozent': 'Result'}
)
vote.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0})
vote.update_mapboxes(
    center_lat=51.5,
    center_lon=10.25,
    zoom=4.6
)


## Plot Voting-results in form of pie chart:
# want for entire Germany, instead of states:
vote_germ=data[data.Gebietsnummer==99]
vote_germ = vote_germ[vote_germ.Stimme==1]
vote_germ=vote_germ[vote_germ.Gruppenart=="Partei"]
vote_germ=vote_germ[vote_germ.Gebietsname=="Bundesgebiet"]

# cleaning 
#(nan --> 0
vote_germ['Prozent'] = vote_germ['Prozent'].fillna(0)

# , --> .
vote_germ['Prozent'] = (vote_germ['Prozent'].replace(',', '.', regex=True).astype(float))

# string --> int
vote_germ['Prozent'] = pd.to_numeric(vote_germ['Prozent'])

#print(vote_germ.to_string())



# 47 different states. Diving into: SPD, CDU/CSU, AfD, and "Others":
#vote_germ.loc[vote_germ['Gruppenname'] == "CDU", 'Gruppenname'] = "CDU/CSU"
#vote_germ.loc[vote_germ['Gruppenname'] == "CSU", 'Gruppenname'] = "CDU/CSU"

vote_germ.loc[vote_germ['Prozent'] < 6, 'Gruppenname'] = "Other"
vote_germ.loc[vote_germ['Gruppenname'] == "FDP", 'Gruppenname'] = "Other"
vote_germ.loc[vote_germ['Gruppenname'] == "GRÜNE", 'Gruppenname'] = "Other"


    
    
vote_chart = px.pie(vote_germ, values='Prozent', names='Gruppenname', color='Gruppenname',
                    color_discrete_map={'SPD':'#E3000F',
                                        'CDU':'32302e',
                                        'CSU':'#0080c8',
                                        'AfD':'009ee0',
                                        'Other':'grey'})

#vote_chart.show()




## Build web app with dash
app = dash.Dash(__name__)

app.layout = lambda: html.Div([
    # H1-Header
    html.H1(children="Does voting against vaccinations mean voting for COVID?",
            style={'textAlign': 'center', 'fontFamily': 'Helvetica, Arial, sans-serif'}),
    html.Div([
        html.Div([
            dcc.Graph(figure=vacc)
        ], style={'width': '33%', 'float': 'left'}),
        html.Div([
            dcc.Graph(figure=cov)
        ], style={'width': '33%', 'float': 'left'}),
        html.Div([
            dcc.Graph(figure=vote)
        ], style={'width': '33%', 'float': 'left'})
    ]),
    html.Div([
        html.Div([
            dcc.Graph(figure=vacc)
        ], style={'width': '33%', 'float': 'left'}),
        html.Div([
            dcc.Graph(figure=cov)
        ], style={'width': '33%', 'float': 'left'}),
        html.Div([
            dcc.Graph(figure=vote)
        ], style={'width': '33%', 'float': 'left'})
    ])
])


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
    
    
    
    