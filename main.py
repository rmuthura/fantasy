import json

from espn_api.football import League
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
import random


ADP = pd.read_csv('adprankings.csv')
ADP = ADP.drop(['Pos', 'ESPN', 'SLEEPER', 'NFL', 'RTSPORTS'], axis=1)
ADP['Player'] = ADP['Player'].str.replace(r'\s+[A-Z]+\s*\(\d+\)', '', regex=True)

qb = pd.read_csv('qbproj.csv')
rb = pd.read_csv('rbproj1.csv')
rb2 = pd.read_csv('rbproj2.csv')
rb3 = pd.read_csv('rbproj3.csv')
te = pd.read_csv('teproj.csv')
te2 = pd.read_csv('teproj2.csv')
wr = pd.read_csv('wrproj1.csv')
wr2 = pd.read_csv('wrproj2.csv')
wr3 = pd.read_csv('wrproj3.csv')
wr4 = pd.read_csv('wrproj4.csv')

qb['Position'] = 'Quarterback'
qb_df = qb.rename(columns={'Quarterback': 'Name'})
rb['Position'] = 'Running Back'
rb_df = rb.rename(columns={'Running Back': 'Name'})
rb2['Position'] = 'Running Back'
rb2_df = rb2.rename(columns={'Running Back': 'Name'})
rb3['Position'] = 'Running Back'
rb3_df = rb3.rename(columns={'Running Back': 'Name'})
te['Position'] = 'Tight End'
te_df = te.rename(columns={'Tight End': 'Name'})
te2['Position'] = 'Tight End'
te2_df = te2.rename(columns={'Tight End': 'Name'})
wr['Position'] = 'Wide Receiver'
wr_df = wr.rename(columns={'Wide Receiver': 'Name'})
wr2['Position'] = 'Wide Receiver'
wr2_df = wr2.rename(columns={'Wide Receiver': 'Name'})
wr3['Position'] = 'Wide Receiver'
wr3_df = wr3.rename(columns={'Wide Receiver': 'Name'})
wr4['Position'] = 'Wide Receiver'
wr4_df = wr4.rename(columns={'Wide Receiver': 'Name'})

df = pd.concat([qb_df, rb_df, rb2_df, rb3_df, wr_df, wr2_df, wr3_df, wr4_df, te_df, te2_df], ignore_index=True)

pd.set_option('display.max_columns', None)

df_merged = df.merge(ADP[['Player', 'AVG']], left_on='Name', right_on='Player', how='left')

df_merged = df_merged.drop(columns=['Player']).rename(columns={'AVG': 'ADP'})


numeric_cols = df_merged.select_dtypes(include=[np.number])
correlation_matrix = numeric_cols.corr()

plt.figure(figsize=(12, 8))
sns.heatmap(correlation_matrix, annot=True, cmap='coolwarm', fmt=".2f")
plt.title('Correlation Heatmap')
#plt.show()



url1 = 'https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLProjections?week=season&archiveSeason=2024&twoPointConversions=2&passYards=.04&passAttempts=0&passTD=4&passCompletions=0&passInterceptions=-2&pointsPerReception=1&carries=0&rushYards=.1&rushTD=6&fumbles=-2&receivingYards=.1&receivingTD=6&targets=0&fgMade=3&fgMissed=-1&xpMade=1&xpMissed=-1'

headers1 = {
    "x-rapidapi-host": "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com",
    "x-rapidapi-key": "9f6d130153msh1e99001349e0c1bp131a89jsn3e17657541f1"
}
response2 = requests.get(url1, headers=headers1)
data2 = response2.json()
players_data = data2.get('body', {})
playerDataFull = []
for player_id, details in players_data['playerProjections'].items():
    player_data = {
        'Player ID': player_id,
        'Long Name': details.get('longName'),
        'Fantasy Points': (details.get('fantasyPoints')),
        'Position': (details.get('pos'))
    }
    playerDataFull.append(player_data)

df = pd.DataFrame(playerDataFull)

url = "https://tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com/getNFLADP"
querystring = {"adpType": "PPR"}

headers = {
    "x-rapidapi-host": "tank01-nfl-live-in-game-real-time-statistics-nfl.p.rapidapi.com",
    "x-rapidapi-key": "9f6d130153msh1e99001349e0c1bp131a89jsn3e17657541f1"
}

response = requests.get(url, headers=headers, params=querystring)

data = response.json()
players = data["body"]["adpList"]
playerDataFull2 = []
for player in players:
    player_data = {
        'Player ID': player.get('playerID'),
        'ADP': player.get('overallADP')
    }
    playerDataFull2.append(player_data)

df2 = pd.DataFrame(playerDataFull2)

masterChart = pd.merge(df, df2, on='Player ID', how='inner')
masterChart['Fantasy Points'] = pd.to_numeric(masterChart['Fantasy Points'])
masterChart['Fantasy Points'].fillna(0, inplace=True)
finalMasterChart = masterChart.sort_values(by='Fantasy Points', ascending=False)
finalMasterChart['ADP'] = pd.to_numeric(finalMasterChart['ADP'], errors='coerce')
playersHighADP = finalMasterChart[finalMasterChart['ADP'] > 120]
playersHighADP = playersHighADP.sort_values(by='ADP')


qbSorted = finalMasterChart[finalMasterChart['Position'] == 'QB'].sort_values(by='ADP')
rbSorted = finalMasterChart[finalMasterChart['Position'] == 'RB'].sort_values(by='ADP')
wrSorted = finalMasterChart[finalMasterChart['Position'] == 'WR'].sort_values(by='ADP')
teSorted = finalMasterChart[finalMasterChart['Position'] == 'TE'].sort_values(by='ADP')
print(playersHighADP)
qbBaseline = playersHighADP[playersHighADP['Position'] == 'QB'].iloc[0]['Fantasy Points']
print(qbBaseline)
rbBaseline = playersHighADP[playersHighADP['Position'] == 'RB'].iloc[0]['Fantasy Points']
print(rbBaseline)
wrBaseline = playersHighADP[playersHighADP['Position'] == 'WR'].iloc[0]['Fantasy Points']
print(wrBaseline)
teBaseline = playersHighADP[playersHighADP['Position'] == 'TE'].iloc[0]['Fantasy Points']
print(teBaseline)

for index, row in finalMasterChart.iterrows():
    if row['Position'] == 'QB':
        finalMasterChart.at[index, 'VBD'] = row['Fantasy Points'] - qbBaseline
    elif row['Position'] == 'RB':
        finalMasterChart.at[index, 'VBD'] = row['Fantasy Points'] - rbBaseline
    elif row['Position'] == 'TE':
        finalMasterChart.at[index, 'VBD'] = row['Fantasy Points'] - teBaseline
    elif row['Position'] == 'WR':
        finalMasterChart.at[index, 'VBD'] = row['Fantasy Points'] - wrBaseline

finalMasterChart = finalMasterChart.sort_values(by='VBD', ascending= False)
finalMasterChart['Rank'] = np.argsort(finalMasterChart.reset_index(drop=True)
                                      .sort_values(by='VBD', ascending=False)
                                      .index) + 1

finalMasterChart['Diff'] = finalMasterChart['ADP'] - finalMasterChart['Rank']
#print(finalMasterChart[finalMasterChart["Position"] == "WR"].head(50))
print(finalMasterChart.head(25))
list1 = [0,1, 2, 3, 4, 5, 6,7,8,9,10,11]
finalMasterChart = finalMasterChart.drop('Rank', axis=1)
#
def simDraft(teams=12, rounds=13, pickNumber=0):
    draftBoard = [[] for team in range(teams)]
    for roundNumber in range(rounds):
        print(f"\nRound {roundNumber + 1}")
        if roundNumber % 2 == 0:
            order = range(teams)
        else:
            order = range(teams - 1, -1, -1)
        for teamNumber in order:
            if teamNumber == pickNumber:
                while True:
                    print("Best WR\n")
                    print(finalMasterChart[finalMasterChart["Position"] == "WR"].head(10))
                    print("Best RB\n")
                    print(finalMasterChart[finalMasterChart["Position"] == "RB"].head(10))
                    print("Best QB\n")
                    print(finalMasterChart[finalMasterChart["Position"] == "QB"].head(10))
                    print("Best TE\n")
                    print(finalMasterChart[finalMasterChart["Position"] == "TE"].head(10))
                    print("Best Available\n")
                    print(finalMasterChart.head(10))
                    print("Current Team\n")
                    print(draftBoard[teamNumber])
                    print(f"Team {teamNumber + 1}, pick a player: ")
                    pickPlayer = input().strip()
                    if pickPlayer in finalMasterChart['Long Name'].values:
                        finalMasterChart.drop(
                            finalMasterChart[finalMasterChart['Long Name'] == pickPlayer].index, inplace=True
                        )
                        draftBoard[teamNumber].append(pickPlayer)
                        break
                    else:
                        print("Invalid.")
            else:
                bestAvailableADP = finalMasterChart.loc[finalMasterChart['ADP'].idxmin()]
                print(bestAvailableADP)
                draftBoard[teamNumber].append(bestAvailableADP)
                finalMasterChart.drop(
                    finalMasterChart[finalMasterChart['Long Name'] == bestAvailableADP['Long Name']].index, inplace=True
                )
    teams_players = {}
    for teamNumber, teamPicks in enumerate(draftBoard, start=1):
        teams_players[f"Team {teamNumber}"] = teamPicks

    for team, players in teams_players.items():
        print(f"\n{team} draft picks:")
        for player in players:
            print(player)


#simDraft(12,13,1)


def Draft(teams=12, rounds=13):
    draftBoard = [[] for team in range(teams)]
    for roundNumber in range(rounds):
        print(f"\nRound {roundNumber + 1}")
        if roundNumber % 2 == 0:
            order = range(teams)
        else:
            order = range(teams - 1, -1, -1)
        for teamNumber in order:
            while True:
                print(f"Team {teamNumber + 1}, it's your turn to pick.")
                print("Best WR\n")
                print(finalMasterChart[finalMasterChart["Position"] == "WR"].head(10))
                print("Best RB\n")
                print(finalMasterChart[finalMasterChart["Position"] == "RB"].head(10))
                print("Best QB\n")
                print(finalMasterChart[finalMasterChart["Position"] == "QB"].head(10))
                print("Best TE\n")
                print(finalMasterChart[finalMasterChart["Position"] == "TE"].head(10))
                print("Best Available\n")
                print(finalMasterChart.head(10))
                print("Current Team\n")
                print(draftBoard[teamNumber])
                pickPlayer = input(f"Team {teamNumber + 1}, pick a player: ").strip()

                if pickPlayer in finalMasterChart['Long Name'].values:
                    # Remove the player from the draft board
                    finalMasterChart.drop(
                        finalMasterChart[finalMasterChart['Long Name'] == pickPlayer].index, inplace=True
                    )
                    # Add the player to the team's draft picks
                    draftBoard[teamNumber].append(pickPlayer)
                    break
                else:
                    print("Invalid selection. Please choose a valid player name from the list.")

    teams_players = {}
    for teamNumber, teamPicks in enumerate(draftBoard, start=1):
        teams_players[f"Team {teamNumber}"] = teamPicks

    for team, players in teams_players.items():
        print(f"\n{team} draft picks:")
        for player in players:
            print(player)

#Draft(12,13)