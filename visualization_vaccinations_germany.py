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

# figure for vaccination data
def display_vacc_data():
    fig = px.choropleth(data_frame=vacc_data,
                        geojson=germany_states,
                        locations='Bundesland',
                        featureidkey='properties.name',
                        hover_name='Bundesland',
                        hover_data=['Datum', 'Impfquote_gesamt_voll'],
                        color='Impfquote_gesamt_voll',
                        color_continuous_scale=px.colors.diverging.RdYlGn,
                        labels={'Impfquote_gesamt_voll': 'fully vaccinated'}
                        )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0})

    return fig

# Open Germany map as GeoJSON
with urlopen(
        "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json") as file:
    germany_states = json.load(file)

## Build web app with dash
app = dash.Dash(__name__)

figure = display_vacc_data()

app.layout = lambda: html.Div([
    # H1-Header
    html.H1(children="Does voting against vaccinations mean voting for COVID?",
            style={'textAlign': 'center', 'fontFamily': 'Helvetica, Arial, sans-serif'}),
    html.Div([
        html.Div([
            dcc.Graph(
                figure=figure,
                id='vaccination-map')
        ], style={'width': '46%', 'display': 'inline-block', 'verticalAlign': 'top', 'margin': '2%'}),
    ])
])


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
