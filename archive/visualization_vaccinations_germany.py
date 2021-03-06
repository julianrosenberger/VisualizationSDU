import pandas as pd
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
#print(vacc_data.head)
#print(dir(vacc_data))

# get minimum and maximum vaccination rate for whole Germany
minvacc = float(vacc_data["Impfquote_gesamt_voll"].min())
maxvacc = float(vacc_data["Impfquote_gesamt_voll"].max())

## Read-in RKI Covid-Data

# Open Germany map as GeoJSON
with urlopen("https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json") as file:
    germany_states = json.load(file)


fig = px.choropleth_mapbox(
                    mapbox_style='white-bg',
                    data_frame=vacc_data,
                    geojson=germany_states,
                    locations='Bundesland',
                    featureidkey='properties.name',
                    hover_name='Bundesland',
                    hover_data=['Datum', 'Impfquote_gesamt_voll'],
                    color='Impfquote_gesamt_voll',
                    color_continuous_scale=px.colors.sequential.Blues,
                    labels={'Impfquote_gesamt_voll': 'fully vaccinated'}
                    )
fig.update_mapboxes(
    center_lat=51.5,
    center_lon=10.25,
    zoom=4.6
    # ToDo: add maxzoom here
    #layers=list({'maxzoom': '4.6'})
)
#fig.update(
 #   layout_coloraxis_showscale=False
#)
'''fig.update_coloraxes( # https://plotly.com/python/reference/layout/coloraxis/
    cmin=45,
    cmax=95
)'''
fig.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0})

#fig.update_xaxes(rangeslider_thickness=0.2)

## Build web app with dash
app = dash.Dash(__name__)

app.layout = lambda: html.Div([
    # H1-Header
    html.H1(children="Does voting against vaccinations mean voting for COVID?",
            style={'textAlign': 'center', 'fontFamily': 'Helvetica, Arial, sans-serif'}),
    html.Div([
        html.Div([
            dcc.Graph(figure=fig)
        ], style={'width': '33%', 'float': 'left'}),
        html.Div([
            dcc.Graph(figure=fig)
        ], style={'width': '33%', 'float': 'left'}),
        html.Div([
            dcc.Graph(figure=fig)
        ], style={'width': '33%', 'float': 'left'})
    ])
])


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
