import requests
from lxml import html
import pandas as pd
import time
import tqdm

teams_url = "https://www.basketball-reference.com/contracts/"

salary_cap_2024_25 = 140588000

rate_limit = 1.5 * (
    60 / 20
)  # 1.5 times the number of sleeps requested to have 20 requests per minute


def get_teams():
    time.sleep(rate_limit)
    response = requests.get(teams_url)
    tree = html.fromstring(response.content)
    # get div with id="div_team_summary"
    teams = tree.xpath("//div[@id='div_team_summary']")
    # find tbody within teams
    teams = teams[0].xpath(".//tbody")
    # get all tr elements
    teams = teams[0].xpath(".//tr")
    data = []
    # get the team names and data
    for i, team in enumerate(teams):
        #    data-stat="team_name"
        team_name = team.xpath(".//td[@data-stat='team_name']/a/text()")
        y1_salary = team.xpath(".//td[@data-stat='y1']/text()")
        data.append([team_name] + [y1_salary])

    teams = pd.DataFrame(data, columns=["Team", "Y1_Salary"])
    return teams


teams_df = get_teams()
teams_df.to_csv("teams_salaries.csv", index=False)


# get the players salaries
def get_players():
    # rate limit
    time.sleep(rate_limit)

    # get the teams
    response = requests.get(teams_url)
    tree = html.fromstring(response.content)
    # get div with id="div_team_summary"
    teams = tree.xpath("//div[@id='div_team_summary']")
    # find tbody within teams
    teams = teams[0].xpath(".//tbody")
    # get all tr elements
    teams = teams[0].xpath(".//tr")
    data = []
    # get the team names and data
    for i, team in enumerate(teams):
        # for each team go to the team page
        team_link = team.xpath(".//td[@data-stat='team_name']/a/@href")
        team_link = "https://www.basketball-reference.com" + team_link[0]

        # rate limit
        time.sleep(rate_limit)

        response = requests.get(team_link)
        tree = html.fromstring(response.content)
        # find div with "all_contracts"
        contracts = tree.xpath("//div[@id='all_contracts']")
        # get the table tbody
        contracts = contracts[0].xpath(".//tbody")
        # get all tr elements
        contracts = contracts[0].xpath(".//tr")
        # get the player names and salaries
        for j, player in enumerate(contracts):
            player_name = player.xpath(".//td[@data-stat='player']/a/text()")
            # get player link
            player_link = player.xpath(".//td[@data-stat='player']/a/@href")
            player_age = player.xpath(".//td[@data-stat='age_today']/text()")
            salary = player.xpath(".//td[@data-stat='y1']/text()")
            data.append([player_name] + [player_link] + [player_age] + [salary])

    players = pd.DataFrame(data, columns=["Player", "Link", "Age", "Salary"])

    return players


players_df = get_players()
players_df.to_csv("players_salaries.csv", index=False)
print(players_df.head())
