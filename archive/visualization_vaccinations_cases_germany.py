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

#covid_data = pd.read_excel("https://www.rki.de/DE/Content/InfAZ/N/Neuartiges_Coronavirus/Daten/Fallzahlen_Inzidenz_aktualisiert.xlsx?__blob=publicationFile")
#print(covid_data.head)

# get minimum and maximum vaccination rate for whole Germany
minvacc = float(vacc_data["Impfquote_gesamt_voll"].min())
maxvacc = float(vacc_data["Impfquote_gesamt_voll"].max())

## Read-in RKI Covid-Data
with urlopen("https://raw.githubusercontent.com/julianrosenberger/VisualizationSDU/main/data/RKI_Corona_Bundesl%25C3%25A4nder.csv?token=ARUOLO4QDTFFNXDTZP2EBN3BW4E7S") as cases:
    covid_data = pd.read_csv(cases)
    #print(covid_data.head)

# Open Germany map as GeoJSON
with urlopen("https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json") as file:
    germany_states = json.load(file)

# Read-in Covid-Data (States)
with urlopen("https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/Coronaf%C3%A4lle_in_den_Bundesl%C3%A4ndern/FeatureServer/0/query?where=1%3D1&outFields=LAN_ew_AGS,LAN_ew_GEN,Aktualisierung,cases7_bl_per_100k,death7_bl,cases7_bl_per_100k_txt,cases7_bl&outSR=4326&f=json") as cases_states:
    covid_states = json.load(cases_states)

df = pd.json_normalize(covid_states, record_path=['features'])
print(df.head(16))




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
                    labels={'Impfquote_gesamt_voll': 'fully vaccinated', 'Bundesland': 'state'}
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
#fig.show()

#fig.update_xaxes(rangeslider_thickness=0.2)

## create choropleth map for cases in germany

cov_static = px.choropleth_mapbox(
    mapbox_style='white-bg',
    data_frame=covid_data,
    geojson=germany_states,
    locations='LAN_ew_GEN',
    featureidkey='properties.name',
    hover_name='LAN_ew_GEN',
    hover_data=['Aktualisierung', 'cases7_bl_per_100k'],
    color='cases7_bl_per_100k',
    color_continuous_scale=px.colors.sequential.YlOrRd,
    labels={'cases7_bl_per_100k': '7-day incidence', 'LAN_ew_GEN': 'state'}
)
cov_static.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0})
cov_static.update_mapboxes(
    center_lat=51.5,
    center_lon=10.25,
    zoom=4.6
    # ToDo: add maxzoom here
    #layers=list({'maxzoom': '4.6'})
)

cov_daily = px.choropleth_mapbox(
    mapbox_style='white-bg',
    data_frame=df,
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
cov_daily.update_layout(
        margin={"r": 0, "t": 0, "l": 0, "b": 0})
cov_daily.update_mapboxes(
    center_lat=51.5,
    center_lon=10.25,
    zoom=4.6
    # ToDo: add maxzoom here
    #layers=list({'maxzoom': '4.6'})
)

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
            dcc.Graph(figure=cov_static)
        ], style={'width': '33%', 'float': 'left'}),
        html.Div([
            dcc.Graph(figure=cov_daily)
        ], style={'width': '33%', 'float': 'left'})
    ])
])


if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
