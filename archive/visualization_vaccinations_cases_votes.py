import pandas as pd
import pandasql
import dash
from dash.dependencies import Input, Output
from dash import dcc
from dash import html
import plotly.express as px
from urllib.request import urlopen
import json

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
with urlopen("https://raw.githubusercontent.com/julianrosenberger/VisualizationSDU/main/data/kerg2.csv?token=ARUOLO332LU5QYK5OW3OF6LBW4POK") as f:
    data = pd.read_csv(f, delimiter=';', skiprows=9, usecols=['Gebietsnummer', 'Gebietsname', 'Gruppenart', 'Gruppenname', 'Gruppenreihenfolge', 'Stimme',	'Prozent'])

parties = ["SPD", "GRÜNE", "CDU", "AfD"]

voting_results = pd.DataFrame(columns=['StateID', 'State', 'Party', 'Result'])
#winners = pd.DataFrame(columns=['State', 'Party', 'Result'])

for i in range(len(data)):
    for state_id in range(1, 17):
        for party in parties:
            if state_id == 9:
                parties[2] = "CSU"
            else:
                parties[2] = "CDU"

            if data.loc[i, 'Gebietsnummer'] == state_id and data.loc[i, 'Gruppenname'] == party and data.loc[i, 'Stimme'] == 1:
                voting_results = voting_results.append({'StateID': data.loc[i, 'Gebietsnummer'],
                                                        'State': data.loc[i, 'Gebietsname'],
                                                        'Party': data.loc[i, 'Gruppenname'],
                                                        'Result': data.loc[i, 'Prozent']},
                                                       ignore_index=True)

                winners = pandasql.sqldf("SELECT State, Party, MAX(Result) FROM voting_results GROUP BY StateID")

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
    data_frame=voting_results,
    geojson=germany_states,
    locations='State',
    featureidkey='properties.name',
    hover_name='State',
    hover_data={'State': False,
                'Party': True,
                'Result': ':.2f%'},
    color='Result',
    color_continuous_scale=px.colors.sequential.YlOrRd,
    #labels={'attributes.cases7_bl_per_100k': '7-day incidence', 'attributes.LAN_ew_GEN': 'State', 'attributes.death7_bl': '7-day deaths'}
)
vote.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0})
vote.update_mapboxes(
    center_lat=51.5,
    center_lon=10.25,
    zoom=4.6
)


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
    ])
])


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
