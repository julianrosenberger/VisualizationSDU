import pandas as pd
from urllib.request import urlopen

with urlopen("https://raw.githubusercontent.com/julianrosenberger/VisualizationSDU/main/data/kerg2.csv?token=ARUOLO332LU5QYK5OW3OF6LBW4POK") as f:
    data = pd.read_csv(f, delimiter=';', skiprows=9, usecols=['Gebietsnummer', 'Gebietsname', 'Gruppenart', 'Gruppenname', 'Gruppenreihenfolge', 'Stimme',	'Prozent'])

parties = ["SPD", "GRÜNE", "CDU", "AfD"]

voting_results = pd.DataFrame(columns = ['StateID', 'State', 'Party', 'Result'])

for state_id in range(1, 16):
    for party in parties:
        if state_id == 9:
            parties[2] = "CSU"
        else:
            parties[2] = "CDU"

for i in range(len(data)):
    for state_id in range(1, 16):
        for party in parties:
            if state_id == 9:
                parties[2] = "CSU"
            else:
                parties[2] = "CDU"

            if data.loc[i, 'Gebietsnummer'] == state_id and data.loc[i, 'Gruppenname'] == party and data.loc[i, 'Stimme'] == 1:
                voting_results = voting_results.append({'StateID': data.loc[i, 'Gebietsnummer'], 'State': data.loc[i, 'Gebietsname'], 'Party': data.loc[i, 'Gruppenname'], 'Result': data.loc[i, 'Prozent']}, ignore_index=True)