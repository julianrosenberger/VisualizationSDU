import pandas as pd
import dash
# import dash_core_components as dcc #this had to be changed
from dash import dcc
# import dash_html_components as html #this as well
from dash import html
import plotly.express as px
from urllib.request import urlopen
import json

pd.options.mode.chained_assignment = None  # default='warn'
px.set_mapbox_access_token(open("mapbox_token.txt").read())

### Get Data from Different Sources ###
## get vaccination data from rki vaccination github repo:
# (https://github.com/robert-koch-institut/COVID-19-Impfungen_in_Deutschland)
url_vacc_data = "https://raw.githubusercontent.com/robert-koch-institut/COVID-19-Impfungen_in_Deutschland/master/Aktuell_Deutschland_Impfquoten_COVID-19.csv"
# read-in data from csv-file (filter out Deutschland & Bundesressorts)
vacc_data = pd.read_csv(url_vacc_data, skiprows=[1, 18])

## Read-in Vacc-History
with urlopen("https://raw.githubusercontent.com/owid/covid-19-data/master/public/data/vaccinations/vaccinations.csv") as vacc_his:
    vacc_history = pd.read_csv(vacc_his)

# Clean-up Vacc-History
vacc_history = vacc_history[vacc_history.location == "Germany"]
fully_vacc_germany = vacc_history[["date", "people_fully_vaccinated_per_hundred"]]
fully_vacc_germany = fully_vacc_germany[fully_vacc_germany.date >= "2021-06-07"]

## Read-in Covid-Data (States)
with urlopen(
        "https://services7.arcgis.com/mOBPykOjAyBO2ZKk/arcgis/rest/services/Coronaf%C3%A4lle_in_den_Bundesl%C3%A4ndern/FeatureServer/0/query?where=1%3D1&outFields=LAN_ew_AGS,LAN_ew_GEN,Aktualisierung,cases7_bl_per_100k,death7_bl,cases7_bl_per_100k_txt,cases7_bl&outSR=4326&f=json") as cases_states:
    covid_states = json.load(cases_states)

covid_data = pd.json_normalize(covid_states, record_path=['features'])

## Read-in historical Case-Data
with urlopen(
        "https://raw.githubusercontent.com/jgehrcke/covid-19-germany-gae/master/cases-rki-by-state.csv") as cov_history:
    covid_history = pd.read_csv(cov_history)

# Clean-up historical Case-Data
covid_history_germany = covid_history[["time_iso8601", "sum_cases"]]
covid_history_germany.sum_cases = covid_history_germany.sum_cases.astype(int)
covid_history_june = covid_history_germany[covid_history_germany["time_iso8601"] > "2021-06-06T17:00:00+0000"]
covid_daily_cases_june = covid_history_june[["time_iso8601", "sum_cases"]]
covid_daily_cases_june["daily_cases"] = covid_daily_cases_june.sum_cases.diff().fillna(1686).astype(int)

## Read in Voting-Results
with urlopen("https://raw.githubusercontent.com/julianrosenberger/VisualizationSDU/main/data/kerg2.csv?token=ARUOLO4UXYPQGNQROTOGVL3BZVLQI") as f:
    data = pd.read_csv(f, delimiter=';', skiprows=9,
                       usecols=['Gebietsnummer', 'Gebietsname', 'UegGebietsnummer', 'Gruppenart', 'Gruppenname',
                                'Gruppenreihenfolge', 'Stimme', 'Prozent'])

# Clean-up Voting-results
# Deleting where Gruppenart!=Partei
df_clear = data[data.Gruppenart == "Partei"]
# deleting Stimme==1:
df_clear2 = df_clear[df_clear.Stimme == 2]
# Grouped dataframe with only the states 1-16 (both incl.)
df_clear3 = df_clear2[df_clear2.Gebietsnummer < 17]
# Make sure Gebietsnummer belongs to state
df_clear4 = df_clear3[df_clear3.UegGebietsnummer == 99]
df_clear = df_clear4
# (nan --> 0
df_clear['Prozent'] = df_clear['Prozent'].fillna(0)
# , --> .
df_clear['Prozent'] = (df_clear['Prozent'].replace(',', '.', regex=True).astype(float))
# string --> int
df_clear['Prozent'] = pd.to_numeric(df_clear['Prozent'])
# Gruping by state:
df_group = df_clear.groupby('Gebietsnummer')
maximums = df_group['Prozent'].max()
winners = df_clear.loc[df_clear.groupby(['Gebietsnummer'])['Prozent'].idxmax()].reset_index(drop=True)

## Voting Results based on https://www.zeit.de/politik/deutschland/2021-09/wahlergebnisse-bundestagswahl-2021-wahlkreise-karte-deutschland-live
votes = {"Party": ["SPD", "CDU/CSU", "AfD", "Other"], "Result": [25.70, 24.10, 10.30, 39.90]}
vote_germ = pd.DataFrame(votes)

### Map Data ###
## Open Germany map as GeoJSON
with urlopen(
        "https://raw.githubusercontent.com/isellsoap/deutschlandGeoJSON/main/2_bundeslaender/2_hoch.geo.json") as file:
    germany_states = json.load(file)

### Visualizations ###
## Plot Vaccination Map
vacc = px.choropleth_mapbox(
    mapbox_style='light',
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
    zoom=4.55
)
vacc.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

## Plot Vaccination Line-Chart
vaccination_history = px.line(
    fully_vacc_germany,
    x='date',
    y='people_fully_vaccinated_per_hundred',
    hover_data={
        'people_fully_vaccinated_per_hundred': ':.1f'
    },
    labels={"people_fully_vaccinated_per_hundred": "Proportion of vaccinated", "date": "Date"}
)
vaccination_history.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0},
    yaxis_range=[20, 100],
    yaxis_showgrid=True,
)

## Covid-Data ##
# Plot Covid-Map
cov = px.choropleth_mapbox(
    mapbox_style='light',
    data_frame=covid_data,
    geojson=germany_states,
    locations='attributes.LAN_ew_GEN',
    featureidkey='properties.name',
    hover_name='attributes.LAN_ew_GEN',
    hover_data={'attributes.LAN_ew_GEN': False,
                'attributes.cases7_bl_per_100k': ':.1f',
                'attributes.death7_bl': False},
    color='attributes.cases7_bl_per_100k',
    color_continuous_scale=px.colors.sequential.YlOrRd,
    labels={'attributes.cases7_bl_per_100k': '7-day incidence', 'attributes.LAN_ew_GEN': 'State',
            'attributes.death7_bl': '7-day deaths'}
)
cov.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)
cov.update_mapboxes(
    center_lat=51.5,
    center_lon=10.25,
    zoom=4.55
)
# Bar Chart for historical data
cov_history = px.bar(
    covid_daily_cases_june,
    x='time_iso8601',
    y='daily_cases',
    hover_data={
        'daily_cases': ':.0f'
    },
    labels={'time_iso8601': 'Date', 'daily_cases': 'Daily Cases'}
)
cov_history.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)

## Voting Data ##
# Plot Voting-results
vote = px.choropleth_mapbox(
    mapbox_style='light',
    data_frame=winners,
    geojson=germany_states,
    locations='Gebietsname',
    featureidkey='properties.name',
    hover_name='Gebietsname',
    hover_data={'Gebietsname': False,
                'Gruppenname': True,
                'Prozent': ':.1f'},
    color='Gruppenname',
    color_discrete_map={'SPD': "#E3000F",
                        "CDU": "#000",
                        "CSU": "#000",
                        "AfD": "#009ee0"},
    labels={'Gebietsname': 'State', 'Gruppenname': 'Winner', 'Prozent': 'Result'},
)
vote.update_layout(
    margin={"r": 0, "t": 0, "l": 0, "b": 0}
)
vote.update_mapboxes(
    center_lat=51.5,
    center_lon=10.25,
    zoom=4.55
)

## Voting Results Pie-Chart
vote_chart = px.pie(vote_germ,
                    values='Result',
                    names='Party',
                    color='Party',
                    color_discrete_map={'SPD': '#E3000F',
                                        'CDU/CSU': '#000',
                                        'AfD': '009ee0',
                                        'Other': '#ccc'}
                    )
vote_chart.update_layout(
    margin={"r": 10, "t": 10, "l": 10, "b": 10},
    showlegend=True,
)

### Build web app with dash ###
app = dash.Dash(__name__)

app.layout = html.Div(children=[
    # H1-Header
    html.Div([
        html.Img(src="https://www.sdu.dk/-/media/files/nyheder/logoer/sdu_black_rgb_png.png")],
        className='img-container'),
    html.H1(children="Does voting against vaccinations mean voting for COVID?",
            style={'textAlign': 'center', 'fontFamily': 'Helvetica, Arial, sans-serif'}),
    html.H3(children="By Julian Rosenberger and Sarah Stougaard", className="authors"),
    html.Div([
        html.Div([
            html.H3("Fully Vaccinated People in Germany (%)"),
            html.Hr(className="solid"),
            dcc.Graph(figure=vacc)
        ]),
        html.Div([
            html.H3("7-day Incidence Germany (per 100k)"),
            html.Hr(className="solid"),
            dcc.Graph(figure=cov)
        ]),
        html.Div([
            html.H3("Voting Results Germany 2021 (%)"),
            html.Hr(className="solid"),
            dcc.Graph(figure=vote)
        ])
    ], className='container'),
    html.Div([
        html.Div([
            html.H3("Proportion of Fully Vaccinated Germans (%)"),
            html.Hr(className="solid"),
            dcc.Graph(figure=vaccination_history)
        ]),
        html.Div([
            html.H3("Daily Cases Germany", className="dailycases"),
            html.Hr(className="solid"),
            dcc.Graph(figure=cov_history)
        ]),
        html.Div([
            html.H3("Voting Results Germany 2021"),
            html.Hr(className="solid"),
            dcc.Graph(figure=vote_chart)
        ]),
    ], className='container'),
])

if __name__ == '__main__':
    app.run_server(debug=True, port=8080)
