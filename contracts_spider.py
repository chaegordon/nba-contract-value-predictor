import requests
from lxml import html
import pandas as pd
import time
import tqdm
import re
import numpy as np

teams_url = "https://www.basketball-reference.com/contracts/"

salary_cap_2024_25 = 140588000

rate_limit = 1.5 * (
    60 / 20
)  # 1.5 times the number of sleeps requested to have 20 requests per minute


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
    # teams = teams[0:1]  # only get the first team for testing
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
        # contracts = contracts[0:10]  # only get the first 10 player for testing
        # get the player names and salaries
        for j, player in enumerate(contracts):
            player_name = player.xpath(".//th[@data-stat='player']/a/text()")
            # get player link
            player_link = player.xpath(".//th[@data-stat='player']/a/@href")
            player_age = player.xpath(".//td[@data-stat='age_today']/text()")
            salary = player.xpath(".//td[@data-stat='y1']/text()")
            data.append([player_name] + [player_link] + [player_age] + [salary])

    players = pd.DataFrame(data, columns=["Player", "Link", "Age", "Salary"])

    # drop rows with missing values for Link or Salary
    players = players.applymap(
        lambda x: np.nan if isinstance(x, list) and len(x) == 0 else x
    )
    players = players.dropna(subset=["Link", "Salary"])
    # NB: will lose waived players, and those without a salary !!

    # save to csv
    players.to_csv("players.csv", index=False)

    return players


def get_player_stats():
    players_df = get_players()
    # remove list brackets
    for col in players_df.columns:
        try:
            players_df[col] = players_df[col].apply(
                lambda x: x[0] if isinstance(x, list) and len(x) > 0 else x
            )
        except Exception as e:
            print(f"Error trying to de-list column {col}")
            # print the error
            print(f"Error: {e}")
            print(players_df[col].head())
            # loop over all the values and get the types of the elements
            for i, x in enumerate(players_df[col]):
                # if not a list, print the type
                if not isinstance(x, list):
                    print(i, type(x))

    # strip $ from Salary column and convert to float
    players_df["Salary"] = (
        players_df["Salary"].str.replace("$", "").str.replace(",", "")
    ).astype(float)
    for i, player in players_df.iterrows():
        player_link = (
            "https://www.basketball-reference.com" + player["Link"] + "/splits/2024"
        )
        # remove ".html"
        player_link = player_link.replace(".html", "")
        print(player_link)
        time.sleep(rate_limit)
        response = requests.get(player_link)
        tree = html.fromstring(response.content)

        # Height and weight
        height_weight = tree.xpath("//p/text()[contains(., 'cm')]")
        # Use regex to extract numbers from the string
        try:
            cm, kg = map(int, re.findall(r"\d+", height_weight[0]))
            players_df.at[i, "Height_cm"] = float(cm)
            players_df.at[i, "Weight_kg"] = float(kg)
        except Exception as e:
            print(
                f"Error trying to extract height and weight for player {player['Player']}"
            )
            # print the error
            print(f"Error: {e}")
            print(height_weight)
            try:
                cm = int(re.findall(r"\d+", height_weight[0])[0])
                kg = pd.NA
                players_df.at[i, "Height_cm"] = float(cm)
                players_df.at[i, "Weight_kg"] = kg
            except Exception as e:
                print(f"Error trying to extract height for player {player['Player']}")
                # print the error
                print(f"Error: {e}")
                print(height_weight)
        # Game Splits Stats
        # find div with "all_per_game"
        stats = tree.xpath("//td[@data-stat and @class='right ']")
        # take first 29 elements only (this year stats)
        stats = stats[0:29]
        for j, td in enumerate(stats):
            data_stat = td.get("data-stat")  # Get the data-stat attribute
            text_value = (
                td.text_content().strip()
            )  # Get the text content (strip any extra spaces)
            players_df.at[i, data_stat] = float(text_value)

    # convert plus_minus to float
    players_df["plus_minus_per_200_poss"] = players_df[
        "plus_minus_per_200_poss"
    ].astype(float)

    # print(players_df.head())
    # print(players_df.dtypes)
    return players_df


players_df = get_player_stats()
players_df.to_csv("players_stats.csv", index=False)
