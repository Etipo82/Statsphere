import requests
import streamlit as st
import datetime
import os
import json
import pandas as pd
import plotly.express as px
from pandas.api.types import CategoricalDtype
from streamlit_lottie import st_lottie
import altair as alt
from PIL import Image
import math
import numpy as np
import sqlite3
from streamlit_option_menu import option_menu



st.set_page_config(page_title="StatSphere", page_icon=":basketball:", layout="wide")
# Import the custom font
st.markdown('<link href="https://fonts.googleapis.com/css2?family=Orbitron&display=swap" rel="stylesheet">', unsafe_allow_html=True)


selected = option_menu(
    menu_title="StatSphere",
    options=["Home", "Game Viewer", "Era Showdown", "Performance Visualizer", "Stat Stars"],
    icons=["house", "calendar-date", "clipboard-data", "graph-up-arrow", "clipboard-data-fill"],
    menu_icon="display",
    default_index=0,
    orientation="horizontal",
)

#Use local CSS
def local_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style/style.css")


baseUrl = 'https://www.balldontlie.io/api/v1/'
playerSearch = 'players/?search='
allPlayers = 'players'
getStats = 'stats'
getTeam = 'teams'
seasonAverages = 'season_averages'
games = 'games'


def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)
    

# Connect to the SQLite database
conn = sqlite3.connect('nba_data.db')
c = conn.cursor()

# Fetch the players data from the database
c.execute('SELECT id, first_name, last_name, full_name, team_id, team_name FROM players')
players_data = c.fetchall()

# Fetch the player-team mapping data from the database
#c.execute('SELECT player_id, team_id FROM player_team_map')
#player_team_map_data = c.fetchall()

# Fetch the teams data from the database
c.execute('SELECT id, abbreviation, city, conference, division, full_name, name FROM teams')
teams_data = c.fetchall()

# Fetch the season stats data from the database
c.execute('SELECT id, player_id, season, pts, reb, ast, stl, blk, turnover, pf, fgm, games_played, fga, fg3m, fg3a, ftm, fta, oreb, dreb, fg_pct, fg3_pct, ft_pct FROM season_stats')
season_stats_data = c.fetchall()

# Close the database connection
conn.close()

# Create a DataFrame for players
# Update the players_columns list to match the actual columns in players_data
players_columns = ['id', 'first_name', 'last_name', 'full_name', 'team_id', 'team_name']
all_players = pd.DataFrame(players_data, columns=players_columns)

# Create a list of player names
#player_names = all_players['first_name'] + ' ' + all_players['last_name']
player_names = all_players['full_name']
player_names = player_names.tolist()

# Create a DataFrame for teams
teams_columns = ['id', 'abbreviation', 'city', 'conference', 'division', 'full_name', 'name']
all_teams = pd.DataFrame(teams_data, columns=teams_columns)

# Create a DataFrame for season stats
season_stats_columns = ['id', 'player_id', 'season', 'pts', 'reb', 'ast', 'stl', 'blk', 'turnover', 'pf', 'fgm', 'games_played', 'fga', 'fg3m', 'fg3a', 'ftm', 'fta', 'oreb', 'dreb', 'fg_pct', 'fg3_pct', 'ft_pct']
all_season_stats = pd.DataFrame(season_stats_data, columns=season_stats_columns)

# Create a dictionary to map player IDs to player names
#player_id_to_name = {player['id']: player['first_name'] + ' ' + player['last_name'] for _, player in all_players.iterrows()}

# Create a dictionary to map player IDs to player names
player_id_to_name = {player['id']: player['full_name'] for _, player in all_players.iterrows()}

def get_db_connection():
    conn = sqlite3.connect('nba_data.db')
    return conn


bball1= load_lottiefile("lottiefiles/basketball graph.json")
bball2= load_lottiefile("lottiefiles/Dunk.json")
vs= load_lottiefile("lottiefiles/vs.json")
vs1= load_lottiefile("lottiefiles/vs.json")
ball = load_lottiefile('lottiefiles/ball.json')
statsphere3d = Image.open('Statsphere-m1.jpg')
statsphere1 = Image.open('Statspherepng.png')
statsphere2 = Image.open('Statsphere.jpg')

st.sidebar.image(statsphere1)


params = {
    'page': 0,
    'per_page': 100,
    'fields': 'id, first_name, last_name, team.full_name'
}


def fetch_weather(city):
    url = "https://weatherapi-com.p.rapidapi.com/current.json"
    querystring = {"q": f"{city}"}
    headers = {
        "X-RapidAPI-Key": "30e1f668b4mshfa785f87edf8117p10c433jsn0abf0b4cea85",
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
    }
    response = requests.request("GET", url, headers=headers, params=querystring)
    return response.json()


def fetch_players(query):
    return requests.get(baseUrl + playerSearch + query).json()


def fetch_stats(player_id, year):
    query = getStats + f"?seasons[]={year}&player_ids[]={player_id}&per_page=200"
    response = requests.get(baseUrl + query).json()
    if response['data']:
        return pd.json_normalize(response['data'])
    else:
        return pd.DataFrame()


def fetch_games(date):
    query = f"{games}?dates[]={date}"
    return requests.get(baseUrl + query).json()


def fetch_stats_game(game_id):
    query = getStats + '?game_ids[]=' + str(game_id)
    return requests.get(baseUrl + query).json()


def display_player_info(player_data, stats_data):
    st.write(f"Name: {player_data['first_name']} {player_data['last_name']}")
    st.write(f"Position: {player_data['position']}")
    st.write(f"Height: {player_data['height_feet']}'{player_data['height_inches']}\"")
    st.write(f"Weight: {player_data['weight_pounds']} lbs")
    st.write(f"Team: {player_data['team']['full_name']}")
    st.write("Stats:")
    st.write(f"Points Per Game: {stats_data['pts']}")
    st.write(f"Rebounds: {stats_data['reb']}")
    st.write(f"Assists: {stats_data['ast']}")
    st.write(f"Turnovers: {stats_data['turnover']}")
    st.write(f"Field Goal Percentage: {stats_data['fg_pct']}")
    st.write(f"Three-Point Percentage: {stats_data['fg3_pct']}")
    st.write(f"Free Throw Percentage: {stats_data['ft_pct']}")


def fetch_season_stats(player_id, year):
    query = f"season_averages?season={year}&player_ids[]={player_id}"
    response = requests.get(baseUrl + query)
    # Check if the response is a valid JSON
    try:
        stats_data = response.json()
    except json.JSONDecodeError:
        print("Error: Invalid JSON response from the API")
        stats_data = {"data": []}  # Return an empty dictionary or handle the error accordingly
    return stats_data


def fetch_stats_era(player_id, year):  # Add the year parameter here
    query = f"{seasonAverages}?season={year}&player_ids[]={player_id}"
    response = requests.get(baseUrl + query).json()
    if response['data']:
        return pd.json_normalize(response['data'])
    else:
        return pd.DataFrame()

# Fetch the player ID from the API
def fetch_player_id(player_name):
    response = requests.get(baseUrl + playerSearch + player_name).json()
    if response['data']:
        return response['data'][0]['id']
    else:
        return None


def fetch_teams():
    # Connect to the SQLite database
    conn = sqlite3.connect('nba_data.db')

    # Fetch the teams data from the database and create a DataFrame
    teams_df = pd.read_sql_query('SELECT * FROM teams', conn)

    # Close the database connection
    conn.close()

    # Create a dictionary with team names as keys and their corresponding IDs as values
    team_names_to_ids = {team['full_name']: team['id'] for _, team in teams_df.iterrows()}
    team_ids_to_names = {team['id']: team['full_name'] for _, team in teams_df.iterrows()}

    return team_names_to_ids, team_ids_to_names


def get_team_id(team_name):
    team_names_to_ids, _ = fetch_teams()
    return team_names_to_ids.get(team_name)


#fanduel computations and display
stat_weights = {
    "fg3m": 1,
    "ast": 1.5,
    "blk": 3,
    "fgm": 2,
    "ftm": 1,
    "reb": 1.2,
    "stl": 3,
    "turnover": -1,
    }

 
def calculate_fanduel_points_total(stats):
    fanduel_points = 0
    for stat, weight in stat_weights.items():
        fanduel_points += stats[stat].sum() * weight
    return fanduel_points


def calculate_fanduel_points(stats):
    fanduel_points = stats.copy()
    for stat, weight in stat_weights.items():
        fanduel_points[stat] = fanduel_points[stat] * weight
    fanduel_points["total"] = fanduel_points[list(stat_weights.keys())].sum(axis=1)
    return fanduel_points


def display_player_info(stats_data):
    try:
        stats = stats_data['data'][0]  # Access the dictionary inside the list
        columns = st.columns(6)
        columns[0].metric("PPG", stats['pts'])
        columns[1].metric("Reb", stats['reb'])
        columns[2].metric("Ast", stats['ast'])
        columns[3].metric("TO", stats['turnover'])
        columns[4].metric("BLK", stats['blk'])
        columns[5].metric("STL", stats['stl'])
    except IndexError:
        pass


def filter_games_by_team(stats, selected_team):
    team_id = get_team_id(selected_team)
    if team_id:
        filtered_stats = stats[(stats["game.home_team_id"] == team_id) | (stats["game.visitor_team_id"] == team_id)]
        print(f"Filtered Stats:\n{filtered_stats}")
        return filtered_stats
    else:
        return stats


def calculate_single_game_fanduel_points(game_stats):
    fanduel_points = (
        (game_stats["pts"] * 1 if game_stats["pts"] is not None else 0)
        + (game_stats["reb"] * 1.2 if game_stats["reb"] is not None else 0)
        + (game_stats["ast"] * 1.5 if game_stats["ast"] is not None else 0)
        + (game_stats["blk"] * 3 if game_stats["blk"] is not None else 0)
        + (game_stats["stl"] * 3 if game_stats["stl"] is not None else 0)
        - (game_stats["turnover"] * 1 if game_stats["turnover"] is not None else 0)
    )
    return fanduel_points

#Functions that will be displayed on Streamlit app
def gameViewer():
    with st.expander("How to use:"):
        st.write('Use the date selector on the left to jump forwards or backwards in the current season,'
                 'or as far back as 2014')
    st.markdown("""
        <h1 style='text-align: center; font-family: "Roboto", sans-serif; font-weight: bold; font-size: 36px;'>
            <span style='color: #1E90FF;'>Game Viewer</span>
        </h1>
        """, unsafe_allow_html=True)
    st.markdown('##')
    game_date_column, schedule_column = st.columns([1,4])
    selected_date = game_date_column.date_input("Select a date")
    with game_date_column:
        st_lottie(
            vs1,
            speed=1,
            loop=True,
            quality='medium',
            height=300,
            width=None,
            key=None,
            )
    if selected_date:
        games_data = fetch_games(selected_date.strftime('%Y-%m-%d'))
        games_list = games_data['data']
        st.write(f"{selected_date} Games")
        for game in games_list:
            game_id = game['id']
            game_stats_data = fetch_stats_game(game_id)['data']

            home_team = game['home_team']['full_name']
            home_city = game['home_team']['city']
            visitor_team = game['visitor_team']['full_name']
            home_score = game['home_team_score']
            visitor_score = game['visitor_team_score']
            status = game['status']

            with schedule_column.expander(f"{home_team} {home_score} :vs: {visitor_team} {visitor_score} ({status})"):
                #weather_data = fetch_weather(home_city)
                #current_temp = weather_data['current']['temp_f']
                #current_condition = weather_data['current']['condition']['text']
                #st.write(f"Current weather in {home_city}: {current_temp}°F, {current_condition}")
                game_stats = []
                for player in game_stats_data:
                    points = player['pts']
                    if points and points >= 10:  # Change the condition to filter players with less than 10 points
                        team = player['team']['full_name']
                        player_name = f"{player['player']['first_name']} {player['player']['last_name']}"
                        rebounds = player['reb']
                        assists = player['ast']
                        game_stats.append((team, player_name, points, rebounds, assists))

                columns = st.columns(2)
                for team, column in zip([home_team, visitor_team], columns):
                    with column:
                        st.write(f"{team} Stats")
                        table_data = []
                        for player_stat in game_stats:
                            if player_stat[0] == team:
                                table_data.append(player_stat[1:])
                                
                        table_df = pd.DataFrame(table_data, columns=['Player', 'Points', 'Rebounds', 'Assists'])
                        st.table(table_df)

    else:
        st.write("Please select a date to view games.")


def playerCharts():
    with st.expander("How to use:"):
        st.write('🏀 Take a trip through NBA history! Select a season as far back as 1947, or '
                 'simply explore the current one. Pick your player and let the games begin! 🚀')
        st.markdown('---')
        st.write("""
                Welcome to the Player Stat Dashboard, your one-stop-shop for all things basketball stats! 🏀 Here's how to become a hoops-stats whiz in no time:

                1. **Pick your baller:** Got a favorite player? Select 'em from the left sidebar, where you can find a nifty dropdown menu. Type away or scroll through to find your star! 🌟

                2. **Choose your season:** Want to reminisce about past glories or stay up-to-date on the latest season? Slide or type in the year on the left sidebar and voilà! 📅

                3. **Season Averages Extravaganza:** Once you've got your player and season, feast your eyes on their full season averages! Points, rebounds, assists – we've got it all! 📊

                4. **Last N Games Flashback:** Curious about a player's recent performances? Pick a number (1-10) in the left column, and watch as their last N games' stats magically appear! Oh, and we didn't forget the FanDuel points! 🎩✨

                5. **Filter by Foes:** Ever wonder how your player fares against specific teams? Use the dropdown menu at the bottom to pick a rival, and we'll reveal all the juicy stats from those games! 🥊

                So, what are you waiting for? Dive in and have a ball exploring your favorite player's stats! 🎉
                """)
    st.markdown("""
        <h1 style='text-align: center; font-family: "Roboto", sans-serif; font-weight: bold; font-size: 36px;'>
            <span style='color: #1E90FF;'>Player Performance Visualizer</span>
        </h1>
        """, unsafe_allow_html=True)
    year = st.sidebar.number_input("Enter Season:", min_value=1905, max_value=2023, value=2022)
    player_names_with_default = ['Lebron James'] + player_names
    # Set the default value using the index parameter (0 for the first item in the list)
    player_lookup = st.sidebar.selectbox("Enter a player name", player_names_with_default, index=0)
    # Define the function to create charts
    chart_column, summary_column = st.columns([4,3])
    def create_chart(stats, chart_option):
        stat_range = chart_column.slider(":level_slider: Filter stat range:", min_value=0, max_value=100, value=(1, 100), step=1)

        if stats.empty:
            st.warning("No stats found for this player and year.")
        else:
            # Convert the 'min' column to a numerical representation (total minutes)
            stats['min'] = stats['min'].apply(
                lambda x: (
                    int(x.split(':')[0]) + round(int(x.split(':')[1]) / 60) if ':' in x else int(x)
                ) if x is not None and x != '' else None
            )

            # Filter out rows where minutes played is 0
            stats = stats[stats['min'] != 0]

            # Create the chart based on the selected option
            if chart_option == 'pts':
                stats = stats[(stats['pts'] >= stat_range[0]) & (stats['pts'] <= stat_range[1])]
                fig = px.bar(stats, x='game.date', y='pts', title=f'Points scored by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

            if chart_option == 'ast':
                stats = stats[(stats['ast'] >= stat_range[0]) & (stats['ast'] <= stat_range[1])]
                fig = px.bar(stats, x='game.date', y='ast', title=f'Assists by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)
            
            if chart_option == "min":
                stats = stats[(stats['min'] >= stat_range[0]) & (stats['min'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='min', title=f'Minutes played by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                )
                st.plotly_chart(fig, use_container_width=True)
               
            if chart_option == "fg_pct":
                stats['fg_pct'] = stats['fg_pct'] * 100
                stats = stats[(stats['fg_pct'] >= stat_range[0]) & (stats['fg_pct'] <= stat_range[1])]
                fig = px.bar(stats, x='game.date', y='fg_pct', title=f'Field goal percentage by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

            if chart_option == "reb":
                stats = stats[(stats['reb'] >= stat_range[0]) & (stats['reb'] <= stat_range[1])]
                fig = px.bar(stats, x='game.date', y='reb', title=f'Rebounds by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)
            
            if chart_option == "fga":
                stats = stats[(stats['fga'] >= stat_range[0]) & (stats['fga'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='fga', title=f'Field Goals Attempted by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)
            
            if chart_option == "blk":
                stats = stats[(stats['blk'] >= stat_range[0]) & (stats['blk'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='blk', title=f'Blocks by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)
            
            if chart_option == "3pm":
                stats = stats[(stats['fg3m'] >= stat_range[0]) & (stats['fg3m'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='fg3m', title=f'3 Pointers Made by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)
            
            if chart_option == "3pa":
                stats = stats[(stats['fg3a'] >= stat_range[0]) & (stats['fg3a'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='fg3a', title=f'3 Pointeds Attempted by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)
            
            if chart_option == "stl":
                stats = stats[(stats['stl'] >= stat_range[0]) & (stats['stl'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='stl', title=f'Steals by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)
            
            if chart_option == "fta":
                stats = stats[(stats['fta'] >= stat_range[0]) & (stats['fta'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='fta', title=f'Free Throws Attempted by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)
          
            if chart_option == "ftm":
                stats = stats[(stats['ftm'] >= stat_range[0]) & (stats['ftm'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='ftm', title=f'Free Throws Made by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)
      
            if chart_option == "3pt_pct":
                stats['fg3_pct'] = stats['fg3_pct'] * 100
                stats = stats[(stats['fg3_pct'] >= stat_range[0]) & (stats['fg3_pct'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='fg3_pct', title=f'3 Point % by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)
            
            if chart_option == "Turnovers":
                stats = stats[(stats['turnover'] >= stat_range[0]) & (stats['turnover'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='turnover', title=f'Turnovers by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

            if chart_option == "Field Goals Made":
                stats = stats[(stats['fgm'] >= stat_range[0]) & (stats['fgm'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='fgm', title=f'FGs Made by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)
        
            # Define the columns for the pie charts
            pts_column, ast_column, reb_column = st.columns(3)

            # Assign each category to a specific column
            category_columns = {
                'Points scored': pts_column,
                'Assists': ast_column,
                'Rebounds': reb_column,
            }

            # Create a dictionary for labels
            labels_dict = {
                'Points scored': ['Under 10', '10-20', '20-30', 'More than 30'],
                'Assists': ['0', '1-3', '4-9', 'More than 10'],
                'Rebounds': ['0', '1-3', '4-9', 'More than 10']
            }

            # Categorize each game based on the stat
            bins = [0, 10, 20, 30, np.inf]

            for option, current_column in category_columns.items():
                stat = chart_options[option]
                labels = labels_dict[option]

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats[stat] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats[stat].groupby(months).sum()

                stats[f'{stat}_range'] = pd.cut(stats[stat], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats[f'{stat}_range'].value_counts()

                # Create a pie chart for month-wise total stats
                pie_chart = px.pie(months_counts.reset_index(), values=stat, names='game.date', title=f'Monthly {option.lower()}')

                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values=f'{stat}_range', names='index', title=f'{option} Range')
                
                # Display the pie charts
                current_column.plotly_chart(pie_chart)
                current_column.plotly_chart(stat_range_pie_chart)
                

    chart_options = {
    "Points scored": "pts",
    "Assists": "ast",
    "Minutes played": "min",
    "Field Goal %": "fg_pct",
    "Field Goals Made": "fgm",
    "Rebounds": "reb",
    "Field Goal Attempted": 'fga',
    "Blocks": 'blk',
    "3-pointers Made": '3pm',
    "3-pointers Attempted": '3pa',
    "3-point %": '3pt_pct',
    "steals": 'stl',
    "Free Throw Attemps": 'fta',
    "Free Throws Made": 'ftm',
    "Turnovers": "Turnovers",
    "Field Goals Made": "Field Goals Made",
    }

    # Define the selected chart as a radio button
    selected_chart = st.sidebar.radio("Select a chart to show:", list(chart_options.keys()), index=0)
    # Get the corresponding stat code from the chart options dictionary
    selected_stat = chart_options[selected_chart]
    try:
        if player_lookup and year:
            player_id = fetch_player_id(player_lookup)
            if player_id:
                stats_data = fetch_season_stats(player_id, year)
                display_player_info(stats_data)
                stats = fetch_stats(player_id, year)
                create_chart(stats, selected_stat)
            else:
                st.warning("Not coming up with anything, check the spelling")
        else:
            st.write("Please enter a player name and year to view stats.")
    except KeyError:
        st.warning('No Data Available for this season')
    
    #Season visualization
    team_names_to_ids, team_ids_to_names = fetch_teams()
    team_names = list(team_names_to_ids.keys())

    st.markdown('---')

    st.header(f":arrows_counterclockwise: Last 10 games for {year} season.")

    column1, column2 = st.columns([1,5])

    stat_column, gif_column = st.columns([1,5])
    
    num_games = column1.number_input(":rewind: Select Quantity", min_value=1, max_value=10, value=3)
    with column1:
        st_lottie(
            ball,
            speed=1,
            loop=True,
            quality='medium',
            height=300,
            width=None,
            key=None,
            )


    try:
        if player_lookup and year:
            player_id = fetch_player_id(player_lookup)
            if player_id:
                stats = fetch_stats(player_id, year)
                
                # Calculate and display the FanDuel points scored (if stats is not empty)
                if not stats.empty:
                    fanduel_points = calculate_fanduel_points(stats)

                    # Calculate and display the last N games based on the number selected
                    fanduel_points_last_n_games = fanduel_points.tail(num_games)
                    stats_last_n_games = stats.tail(num_games)
                    
                    # Display the stats for the last N games
                    with column2:
                        for index, game_stats in stats_last_n_games.iterrows():
                            st.write(f"Game {index + 1}:")
                            columns = st.columns(7)
                            columns[0].metric("Pts", game_stats['pts'])
                            columns[1].metric("Reb", game_stats['reb'])
                            columns[2].metric("Ast", game_stats['ast'])
                            columns[3].metric("TO", game_stats['turnover'])
                            columns[4].metric("BLK", game_stats['blk'])
                            columns[5].metric("3PM", game_stats['fg3m'])

                            fanduel_points = fanduel_points_last_n_games.loc[index, "total"]
                            columns[6].metric("FD Points", fanduel_points)
                        st.markdown('---')
    
                with st.container():
                    with stat_column:
                        selected_team = st.selectbox(":hourglass: Select a team to filter game data:", ["All"] + team_names)
                        filtered_stats = filter_games_by_team(stats, selected_team)
                    with gif_column:
                        st.header("Filtered Stats by Team")
                        team_stats_container = st.columns(7)
                        for index, game_stats in filtered_stats.iterrows():
                            #st.write(f"Game {index + 1}:")
                            team_stats_container[0].metric("Pts", game_stats['pts'])
                            team_stats_container[1].metric("Reb", game_stats['reb'])
                            team_stats_container[2].metric("Ast", game_stats['ast'])
                            team_stats_container[3].metric("TO", game_stats['turnover'])
                            team_stats_container[4].metric("BLK", game_stats['blk'])
                            team_stats_container[5].metric("3PM", game_stats['fg3m'])

                            # Calculate FanDuel points for the current game
                            #try:
                            current_game_fd_points = calculate_single_game_fanduel_points(game_stats)
                            team_stats_container[6].metric("FD Points", current_game_fd_points)
                            #except TypeError:
                            #st.warning('Too far back to calculate')


            else:
                st.warning("Not coming up with anything, check the spelling")
        else:
            st.write("Please enter a player name and year to view stats.")
    except KeyError:
        st.warning('No Data Available for this season')


def playerChart():
    with st.expander("How to use:"):
        st.write('🏀 Take a trip through NBA history! Select a season as far back as 1947, or '
                 'simply explore the current one. Pick your player and let the games begin! 🚀')
        st.markdown('---')
        st.write("""
                Welcome to the Player Stat Dashboard, your one-stop-shop for all things basketball stats! 🏀 Here's how to become a hoops-stats whiz in no time:

                1. **Pick your baller:** Got a favorite player? Select 'em from the left sidebar, where you can find a nifty dropdown menu. Type away or scroll through to find your star! 🌟

                2. **Choose your season:** Want to reminisce about past glories or stay up-to-date on the latest season? Slide or type in the year on the left sidebar and voilà! 📅

                3. **Season Averages Extravaganza:** Once you've got your player and season, feast your eyes on their full season averages! Points, rebounds, assists – we've got it all! 📊

                4. **Last 10 Games Flashback:** Curious about a player's recent performances? Pick a number (1-10) in the left column, and watch as their last N games' stats magically appear! Oh, and we didn't forget the FanDuel points! 🎩✨

                5. **Filter by Foes:** Ever wonder how your player fares against specific teams? Use the dropdown menu at the bottom to pick a rival, and we'll reveal all the juicy stats from those games! 🥊

                So, what are you waiting for? Dive in and have a ball exploring your favorite player's stats! 🎉
                """)
    st.markdown("""
        <h1 style='text-align: center; font-family: "Roboto", sans-serif; font-weight: bold; font-size: 36px;'>
            <span style='color: #1E90FF;'>Player Performance Visualizer</span>
        </h1>
        """, unsafe_allow_html=True)
    year = st.sidebar.number_input("Enter Season:", min_value=1905, max_value=2023, value=2022)
    player_names_with_default = ['Lebron James'] + player_names
    # Set the default value using the index parameter (0 for the first item in the list)
    player_lookup = st.sidebar.selectbox("Enter a player name", player_names_with_default, index=0)
    # Define the function to create charts
    def create_chart(stats, chart_option):
        stat_range = st.slider(":level_slider: Filter stat range:", min_value=0, max_value=100, value=(1, 100), step=1)

        if stats.empty:
            st.warning("No stats found for this player and year.")
        else:
            # Convert the 'min' column to a numerical representation (total minutes)
            stats['min'] = stats['min'].apply(
                lambda x: (
                    int(x.split(':')[0]) + round(int(x.split(':')[1]) / 60) if ':' in x else int(x)
                ) if x is not None and x != '' else None
            )
            # Filter out rows where minutes played is 0
            stats = stats[stats['min'] != 0]
            # Create the chart based on the selected option
            if chart_option == 'pts':
                labels = ['Under 10', '10-20', '20-30', 'More than 30']
                # Categorize each game based on the stat
                bins = [0, 10, 20, 30, np.inf]
                stats = stats[(stats['pts'] >= stat_range[0]) & (stats['pts'] <= stat_range[1])]
                fig = px.bar(stats, x='game.date', y='pts', title=f'Points scored by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats['pts'] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats['pts'].groupby(months).sum()
                bar_chart = px.bar(months_counts.reset_index(), x='game.date', y='pts', title='Points by Month')

                stats['pts_range'] = pd.cut(stats['pts'], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats['pts_range'].value_counts()

                # Create a pie chart for month-wise total stats
                #pie_chart = px.pie(months_counts.reset_index(), values='pts', names='game.date', title='Points by Month')
                #pie_chart = px.pie(months_counts.reset_index(), values='pts', names='game.date', title='Points by Month', hover_data=['pts'])


                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values='pts_range', names='index', title=f'Points scored Range {num_games}')
                
                # Display the pie charts
                chart1_column, chart2_column = st.columns(2)
                with st.container():
                    #chart1_column.plotly_chart(pie_chart)
                    chart1_column.plotly_chart(bar_chart)
                    chart2_column.plotly_chart(stat_range_pie_chart)

            if chart_option == 'ast':
                labels = ['0', '1-4', '5-9', 'More than 10']
                # Categorize each game based on the stat
                bins = [0, 4, 9, 10, np.inf]
                stats = stats[(stats['ast'] >= stat_range[0]) & (stats['ast'] <= stat_range[1])]
                fig = px.bar(stats, x='game.date', y='ast', title=f'Assists by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats['ast'] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats['ast'].groupby(months).sum()  # Corrected here

                stats['ast_range'] = pd.cut(stats['ast'], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats['ast_range'].value_counts()

                # Create a pie chart for month-wise total stats
                pie_chart = px.pie(months_counts.reset_index(), values='ast', names='game.date', title='Assist by Month')

                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values='ast_range', names='index', title=f'Assist by Range {num_games}')
                
                # Display the pie charts
                chart1_column, chart2_column = st.columns(2)
                with st.container():
                    chart1_column.plotly_chart(pie_chart)
                    chart2_column.plotly_chart(stat_range_pie_chart)
    
            if chart_option == "min":
                labels = ['1-10', '11-20', '21-39', 'More than 40']
                # Categorize each game based on the stat
                bins = [10, 20, 30, 40, np.inf]
                stats = stats[(stats['min'] >= stat_range[0]) & (stats['min'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='min', title=f'Minutes played by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                )
                st.plotly_chart(fig, use_container_width=True)

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats['min'] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats['min'].groupby(months).sum()  # Corrected here

                stats['min_range'] = pd.cut(stats['min'], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats['min_range'].value_counts()

                # Create a pie chart for month-wise total stats
                pie_chart = px.pie(months_counts.reset_index(), values='min', names='game.date', title='Minutes by Month')

                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values='min_range', names='index', title=f'Minutes by Range {num_games}')
                
                # Display the pie charts
                chart1_column, chart2_column = st.columns(2)
                with st.container():
                    chart1_column.plotly_chart(pie_chart)
                    chart2_column.plotly_chart(stat_range_pie_chart)

            if chart_option == "fg_pct":
                labels = ['10-19', '20-29', '30-39', '40-49', 'More than 50']
                # Categorize each game based on the stat
                bins = [10, 20, 30, 40, 50, np.inf]
                stats['fg_pct'] = stats['fg_pct'] * 100
                stats = stats[(stats['fg_pct'] >= stat_range[0]) & (stats['fg_pct'] <= stat_range[1])]
                fig = px.bar(stats, x='game.date', y='fg_pct', title=f'Field goal percentage by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats['fg_pct'] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats['fg_pct'].groupby(months).sum()  # Corrected here

                stats['fg_pct_range'] = pd.cut(stats['fg_pct'], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats['fg_pct_range'].value_counts()

                # Create a pie chart for month-wise total stats
                pie_chart = px.pie(months_counts.reset_index(), values='fg_pct', names='game.date', title='FG% by Month')

                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values='fg_pct_range', names='index', title=f'FG% by Range {num_games}')
                
                # Display the pie charts
                chart1_column, chart2_column = st.columns(2)
                with st.container():
                    chart1_column.plotly_chart(pie_chart)
                    chart2_column.plotly_chart(stat_range_pie_chart)

            if chart_option == "reb":
                labels = ['1-3', '4-7', '8-10', 'More than 10']
                # Categorize each game based on the stat
                bins = [3, 7, 10, 11, np.inf]
                stats = stats[(stats['reb'] >= stat_range[0]) & (stats['reb'] <= stat_range[1])]
                fig = px.bar(stats, x='game.date', y='reb', title=f'Rebounds by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats['reb'] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats['reb'].groupby(months).sum()  # Corrected here

                stats['reb_range'] = pd.cut(stats['reb'], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats['reb_range'].value_counts()

                # Create a pie chart for month-wise total stats
                pie_chart = px.pie(months_counts.reset_index(), values='reb', names='game.date', title='Rebound by Month')

                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values='reb_range', names='index', title=f'Rebound by Range {num_games}')
                
                # Display the pie charts
                chart1_column, chart2_column = st.columns(2)
                with st.container():
                    chart1_column.plotly_chart(pie_chart)
                    chart2_column.plotly_chart(stat_range_pie_chart)
                         
            if chart_option == "fga":
                labels = ['1-3', '4-7', '8-10', 'More than 10']
                # Categorize each game based on the stat
                bins = [3, 7, 10, 11, np.inf]
                stats = stats[(stats['fga'] >= stat_range[0]) & (stats['fga'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='fga', title=f'Field Goals Attempted by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats['fga'] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats['fga'].groupby(months).sum()  # Corrected here

                stats['fga_range'] = pd.cut(stats['fga'], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats['fga_range'].value_counts()

                # Create a pie chart for month-wise total stats
                pie_chart = px.pie(months_counts.reset_index(), values='fga', names='game.date', title='FG Attempt by Month')

                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values='fga_range', names='index', title=f'FG Attempt by Range {num_games}')
                
                # Display the pie charts
                chart1_column, chart2_column = st.columns(2)
                with st.container():
                    chart1_column.plotly_chart(pie_chart)
                    chart2_column.plotly_chart(stat_range_pie_chart)
            
            if chart_option == "blk":
                labels = ['1', '2-4', 'More than 4']
                # Categorize each game based on the stat
                bins = [1, 4, 5, np.inf]
                stats = stats[(stats['blk'] >= stat_range[0]) & (stats['blk'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='blk', title=f'Blocks by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats['blk'] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats['blk'].groupby(months).sum()  # Corrected here

                stats['blk_range'] = pd.cut(stats['blk'], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats['blk_range'].value_counts()

                # Create a pie chart for month-wise total stats
                pie_chart = px.pie(months_counts.reset_index(), values='blk', names='game.date', title='blk by Month')

                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values='blk_range', names='index', title=f'blk by Range {num_games}')
                
                # Display the pie charts
                chart1_column, chart2_column = st.columns(2)
                with st.container():
                    chart1_column.plotly_chart(pie_chart)
                    chart2_column.plotly_chart(stat_range_pie_chart)
            
            if chart_option == "3pm":
                labels = ['1-3', '4-7', '8-10', 'More than 10']
                # Categorize each game based on the stat
                bins = [3, 7, 10, 11, np.inf]
                stats = stats[(stats['fg3m'] >= stat_range[0]) & (stats['fg3m'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='fg3m', title=f'3 Pointers Made by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats['fg3m'] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats['fg3m'].groupby(months).sum()  # Corrected here

                stats['3pm_range'] = pd.cut(stats['fg3m'], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats['3pm_range'].value_counts()

                # Create a pie chart for month-wise total stats
                pie_chart = px.pie(months_counts.reset_index(), values='fg3m', names='game.date', title='3pt Made by Month')

                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values='3pm_range', names='index', title=f'3pt Made by Range {num_games}')
                
                # Display the pie charts
                chart1_column, chart2_column = st.columns(2)
                with st.container():
                    chart1_column.plotly_chart(pie_chart)
                    chart2_column.plotly_chart(stat_range_pie_chart)
            
            if chart_option == "3pa":
                labels = ['1-3', '4-7', '8-10', 'More than 10']
                # Categorize each game based on the stat
                bins = [3, 7, 10, 11, np.inf]
                stats = stats[(stats['fg3a'] >= stat_range[0]) & (stats['fg3a'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='fg3a', title=f'3 Pointeds Attempted by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats['fg3a'] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats['fg3a'].groupby(months).sum()  # Corrected here

                stats['3pa_range'] = pd.cut(stats['fg3a'], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats['3pa_range'].value_counts()

                # Create a pie chart for month-wise total stats
                pie_chart = px.pie(months_counts.reset_index(), values='fg3a', names='game.date', title='3pt Attempt by Month')

                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values='3pa_range', names='index', title=f'3pt Attempt by Range {num_games}')
                
                # Display the pie charts
                chart1_column, chart2_column = st.columns(2)
                with st.container():
                    chart1_column.plotly_chart(pie_chart)
                    chart2_column.plotly_chart(stat_range_pie_chart)
            
            if chart_option == "stl":
                labels = ['1', '2-4', 'More than 4']
                # Categorize each game based on the stat
                bins = [1, 4, 5, np.inf]
                stats = stats[(stats['stl'] >= stat_range[0]) & (stats['stl'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='stl', title=f'Steals by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats['stl'] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats['stl'].groupby(months).sum()  # Corrected here

                stats['stl_range'] = pd.cut(stats['stl'], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats['stl_range'].value_counts()

                # Create a pie chart for month-wise total stats
                pie_chart = px.pie(months_counts.reset_index(), values='stl', names='game.date', title='stl by Month')

                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values='stl_range', names='index', title=f'stl by Range {num_games}')
                
                # Display the pie charts
                chart1_column, chart2_column = st.columns(2)
                with st.container():
                    chart1_column.plotly_chart(pie_chart)
                    chart2_column.plotly_chart(stat_range_pie_chart)
            
            if chart_option == "fta":
                labels = ['1-3', '4-7', '8-10', 'More than 10']
                # Categorize each game based on the stat
                bins = [3, 7, 10, 11, np.inf]
                stats = stats[(stats['fta'] >= stat_range[0]) & (stats['fta'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='fta', title=f'Free Throws Attempted by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats['fta'] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats['fta'].groupby(months).sum()  # Corrected here

                stats['fta_range'] = pd.cut(stats['fta'], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats['fta_range'].value_counts()

                # Create a pie chart for month-wise total stats
                pie_chart = px.pie(months_counts.reset_index(), values='fta', names='game.date', title='FT Attempts by Month')

                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values='fta_range', names='index', title=f'FT Attempts by Range {num_games}')
                
                # Display the pie charts
                chart1_column, chart2_column = st.columns(2)
                with st.container():
                    chart1_column.plotly_chart(pie_chart)
                    chart2_column.plotly_chart(stat_range_pie_chart)
          
            if chart_option == "ftm":
                labels = ['1-3', '4-7', '8-10', 'More than 10']
                # Categorize each game based on the stat
                bins = [3, 7, 10, 11, np.inf]
                stats = stats[(stats['ftm'] >= stat_range[0]) & (stats['ftm'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='ftm', title=f'Free Throws Made by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats['ftm'] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats['ftm'].groupby(months).sum()  # Corrected here

                stats['ftm_range'] = pd.cut(stats['ftm'], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats['ftm_range'].value_counts()

                # Create a pie chart for month-wise total stats
                pie_chart = px.pie(months_counts.reset_index(), values='ftm', names='game.date', title='FT Made by Month')

                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values='ftm_range', names='index', title=f'FT Made by Range {num_games}')
                
                # Display the pie charts
                chart1_column, chart2_column = st.columns(2)
                with st.container():
                    chart1_column.plotly_chart(pie_chart)
                    chart2_column.plotly_chart(stat_range_pie_chart)
      
            if chart_option == "3pt_pct":
                labels = ['0-10', '11-20', '21-30', '31-40', '41-50', 'More than 50']
                # Categorize each game based on the stat
                bins = [10, 20, 30, 40, 50, 60, np.inf]
                stats['fg3_pct'] = stats['fg3_pct'] * 100
                stats = stats[(stats['fg3_pct'] >= stat_range[0]) & (stats['fg3_pct'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='fg3_pct', title=f'3 Point % by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats['fg3_pct'] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats['fg3_pct'].groupby(months).sum()  # Corrected here

                stats['3pt_pct_range'] = pd.cut(stats['fg3_pct'], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats['3pt_pct_range'].value_counts()

                # Create a pie chart for month-wise total stats
                pie_chart = px.pie(months_counts.reset_index(), values='fg3_pct', names='game.date', title='3pt % by Month')

                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values='3pt_pct_range', names='index', title=f'3pt % by Range {num_games}')
                
                # Display the pie charts
                chart1_column, chart2_column = st.columns(2)
                with st.container():
                    chart1_column.plotly_chart(pie_chart)
                    chart2_column.plotly_chart(stat_range_pie_chart)
            
            if chart_option == "Turnovers":
                labels = ['1', '2-4', '5-7', 'More than 7']
                # Categorize each game based on the stat
                bins = [1, 4, 7, 8, np.inf]
                stats = stats[(stats['turnover'] >= stat_range[0]) & (stats['turnover'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='turnover', title=f'Turnovers by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats['turnover'] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats['turnover'].groupby(months).sum()  # Corrected here

                stats['turnover_range'] = pd.cut(stats['turnover'], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats['turnover_range'].value_counts()

                # Create a pie chart for month-wise total stats
                pie_chart = px.pie(months_counts.reset_index(), values='turnover', names='game.date', title='turnover by Month')

                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values='turnover_range', names='index', title=f'turnover by Range {num_games}')
                
                # Display the pie charts
                chart1_column, chart2_column = st.columns(2)
                with st.container():
                    chart1_column.plotly_chart(pie_chart)
                    chart2_column.plotly_chart(stat_range_pie_chart)

            if chart_option == "Field Goals Made":
                labels = ['1-3', '4-8', '8-10', 'More than 11']
                # Categorize each game based on the stat
                bins = [3, 8, 10, 11, np.inf]
                stats = stats[(stats['fgm'] >= stat_range[0]) & (stats['fgm'] <= stat_range[1])]
                fig = px.scatter(stats, x='game.date', y='fgm', title=f'FGs Made by {player_lookup} in {year}')
                fig.update_layout(
                    autosize=True,
                    margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                    )
                st.plotly_chart(fig, use_container_width=True)

                # Compute summary statistics
                num_games = stats.shape[0]
                num_games_with_stat = stats[stats['fgm'] > 0].shape[0]  # Number of games with the stat greater than 0
                months = pd.to_datetime(stats['game.date']).dt.month_name()
                months_counts = stats['fgm'].groupby(months).sum()  # Corrected here

                stats['fgm_range'] = pd.cut(stats['fgm'], bins=bins, labels=labels)

                # Count the number of games in each category
                stat_range_counts = stats['fgm_range'].value_counts()

                # Create a pie chart for month-wise total stats
                pie_chart = px.pie(months_counts.reset_index(), values='fgm', names='game.date', title='FG Made by Month')

                # Create a pie chart for stat range
                stat_range_pie_chart = px.pie(stat_range_counts.reset_index(), values='fgm_range', names='index', title=f'FG Made by Range {num_games}')
                
                # Display the pie charts
                chart1_column, chart2_column = st.columns(2)
                with st.container():
                    chart1_column.plotly_chart(pie_chart)
                    chart2_column.plotly_chart(stat_range_pie_chart)
        

                

    chart_options = {
        "Points scored": "pts",
        "Assists": "ast",
        "Minutes played": "min",
        "Field Goal %": "fg_pct",
        "Field Goals Made": "fgm",
        "Rebounds": "reb",
        "Field Goal Attempted": 'fga',
        "Blocks": 'blk',
        "3-pointers Made": '3pm',
        "3-pointers Attempted": '3pa',
        "3-point %": '3pt_pct',
        "steals": 'stl',
        "Free Throw Attemps": 'fta',
        "Free Throws Made": 'ftm',
        "Turnovers": "Turnovers",
        "Field Goals Made": "Field Goals Made",
        }

    # Define the selected chart as a radio button
    selected_chart = st.sidebar.radio("Select a chart to show:", list(chart_options.keys()), index=0)
    # Get the corresponding stat code from the chart options dictionary
    selected_stat = chart_options[selected_chart]
    try:
        if player_lookup and year:
            player_id = fetch_player_id(player_lookup)
            if player_id:
                stats_data = fetch_season_stats(player_id, year)
                display_player_info(stats_data)
                stats = fetch_stats(player_id, year)
                create_chart(stats, selected_stat)
            else:
                st.warning("Not coming up with anything, check the spelling")
        else:
            st.write("Please enter a player name and year to view stats.")
    except KeyError:
        st.warning('No Data Available for this season')
    
    #Season visualization
    team_names_to_ids, team_ids_to_names = fetch_teams()
    team_names = list(team_names_to_ids.keys())

    st.markdown('---')

    st.header(f":arrows_counterclockwise: Last 10 games for {year} season.")

    column1, column2 = st.columns([1,5])

    stat_column, gif_column = st.columns([1,5])
    
    num_games = column1.number_input(":rewind: Select Quantity", min_value=1, max_value=10, value=3)
    with column1:
        st_lottie(
            ball,
            speed=1,
            loop=True,
            quality='medium',
            height=300,
            width=None,
            key=None,
            )


    try:
        if player_lookup and year:
            player_id = fetch_player_id(player_lookup)
            if player_id:
                stats = fetch_stats(player_id, year)
                
                # Calculate and display the FanDuel points scored (if stats is not empty)
                if not stats.empty:
                    fanduel_points = calculate_fanduel_points(stats)

                    # Calculate and display the last N games based on the number selected
                    fanduel_points_last_n_games = fanduel_points.tail(num_games)
                    stats_last_n_games = stats.tail(num_games)
                    
                    # Display the stats for the last N games
                    with column2:
                        for index, game_stats in stats_last_n_games.iterrows():
                            st.write(f"Game {index + 1}:")
                            columns = st.columns(7)
                            columns[0].metric("Pts", game_stats['pts'])
                            columns[1].metric("Reb", game_stats['reb'])
                            columns[2].metric("Ast", game_stats['ast'])
                            columns[3].metric("TO", game_stats['turnover'])
                            columns[4].metric("BLK", game_stats['blk'])
                            columns[5].metric("3PM", game_stats['fg3m'])

                            fanduel_points = fanduel_points_last_n_games.loc[index, "total"]
                            columns[6].metric("Fantasy", fanduel_points)
                        st.markdown('---')
    
                with st.container():
                    with stat_column:
                        selected_team = st.selectbox(":hourglass: Select a team to filter game data:", ["All"] + team_names)
                        filtered_stats = filter_games_by_team(stats, selected_team)
                    with gif_column:
                        st.header("Filtered Stats by Team")
                        team_stats_container = st.columns(7)
                        for index, game_stats in filtered_stats.iterrows():
                            #st.write(f"Game {index + 1}:")
                            team_stats_container[0].metric("Pts", game_stats['pts'])
                            team_stats_container[1].metric("Reb", game_stats['reb'])
                            team_stats_container[2].metric("Ast", game_stats['ast'])
                            team_stats_container[3].metric("TO", game_stats['turnover'])
                            team_stats_container[4].metric("BLK", game_stats['blk'])
                            team_stats_container[5].metric("3PM", game_stats['fg3m'])

                            # Calculate FanDuel points for the current game
                            #try:
                            current_game_fd_points = calculate_single_game_fanduel_points(game_stats)
                            team_stats_container[6].metric("Fantasy", current_game_fd_points)
                            #except TypeError:
                            #st.warning('Too far back to calculate')


            else:
                st.warning("Not coming up with anything, check the spelling")
        else:
            st.write("Please enter a player name and year to view stats.")
    except KeyError:
        st.warning('No Data Available for this season')


def era_compare():
    with st.expander("How to use:"):
        st.write('Feeling nostalgic? Compare players from different eras! '
                 'Select up to 7 players and the years you want to compare them in. '
                 'Witness the epic showdown between the legends of the past and the stars of today!')
    st.markdown("""
        <h1 style='text-align: center; font-family: "Roboto", sans-serif; font-weight: bold; font-size: 36px;'>
            <span style='color: #1E90FF;'>Era Showdown: Legends vs. Rising Stars</span>
        </h1>
        """, unsafe_allow_html=True)
    st.markdown('##')
    num_players = st.sidebar.slider("Select the number of players to compare (1-7):", min_value=1, max_value=7, value=1)

    player_lookup = []
    year_lookup = []
    for i in range(num_players):
        player_name = st.sidebar.selectbox(f"Player {i+1}", options=["Lebron James"] + player_names, format_func=lambda x: x if x else "Lebron james")
        player_year = st.sidebar.number_input(f"Enter the year for Player {i+1}:", min_value=1947, max_value=2023, value=2022, key=f"player_year_{i}")
        player_lookup.append(player_name)
        year_lookup.append(player_year)
    # Rest of the code remains the same

    def create_chart(stats, selected_stat):
        if stats.empty:
            st.warning("No stats found for these players and year.")
        else:
            fig = px.bar(stats, x='player_name', y=selected_stat, color='player_name', title=f'{selected_stat} by player(s)')
            fig.update_layout(
                autosize=True,
                margin=dict(l=0, r=0, t=50, b=0),  # Adjust margins as needed
                )
            st.plotly_chart(fig, use_container_width=True)
    radio_column, graph_column = st.columns([1,4])

    # Main program
    with radio_column:
        selected_stat = st.radio("Select stat:", options=["Games Played", "Points", 
                                                            "Rebounds", "Assists", "Steals",
                                                            "Blocks", "3-Pointers Made", "3-Point Attempts", 
                                                            "3-Point %", "Field Goal %", 
                                                            "Field Goal Attempts", 
                                                            "Field Goal Made", 
                                                            "Free Throw %", "Turnovers"])
    # Define a dictionary to map the selected_stat to the corresponding stat in the stats DataFrame
    stat_map = {
        "Games Played": "games_played",
        "Points": "pts",
        "Rebounds": "reb",
        "Assists": "ast",
        "Steals": "stl",
        "Blocks": "blk",
        "3-Pointers Made" : "fg3m",
        "3-Point Attempts": "fg3a",
        "3-Point %": "fg3_pct",
        "Field Goal %": "fg_pct",
        "Field Goal Attempts": "fga",
        "Field Goal Made": "fgm",
        "Free Throw %": "ft_pct",
        "Turnovers": "turnover",
    }

    with graph_column:
        if all(player_lookup) and any(year_lookup):
            stats = []
            for player_name, year in zip(player_lookup, year_lookup):
                if not player_name:
                    continue

                player_id = fetch_player_id(player_name)
                if player_id:
                    stats_data = fetch_stats_era(player_id, year)  # Pass the year to the fetch_stats function
                    stats_data['player_name'] = player_name
                    stats.append(stats_data)
                else:
                    st.warning(f"Not coming up with anything for {player_name}, check the spelling")

            if stats:
                stats = pd.concat(stats)
                stats = stats.groupby(['player_name']).mean().reset_index()

                # Display the chart for the selected stat
                selected_stat_col = stat_map[selected_stat]
                create_chart(stats, selected_stat_col)

            else:
                st.warning("No stats found for any of the players and year.")
        else:
            st.write("Please enter up to 5 player names & a year to view stats.")


def seasonAverageFilter():
    summary_expander = st.expander("About NBA Stat Stars")
    with summary_expander:
        st.write("""
        Welcome to NBA Stat Stars! 🏀⭐️
        
        Ever wondered who's crushing the court with their dazzling stats? We've got you covered! This app lets you dive into the NBA season averages and discover the players who shine the brightest. Filter through various stats and watch the leaderboard change as you adjust your criteria.
        
        So, what are you waiting for? Unleash your inner basketball analyst, find your favorite players, and let the numbers do the talking! 📊
        """)
    

    st.markdown("""
        <h1 style='text-align: center; font-family: "Roboto", sans-serif; font-weight: bold; font-size: 36px;'>
            <span style='color: #1E90FF;'>Stat Stars</span>
        </h1>
        """, unsafe_allow_html=True)

    # Load the players and season_stats data from the database
    conn = get_db_connection()
    players_df = pd.read_sql_query("SELECT * FROM players", conn)
    stats_df = pd.read_sql_query("SELECT * FROM season_stats", conn)
    conn.close()

    # Create a dictionary to map player IDs to player names
    player_id_to_name = players_df.set_index('id')['full_name'].to_dict()
    player_id_to_team = players_df.set_index('id')['team_name'].to_dict()

    # Define the available fields to filter
    forYear = ['2021', '2022']
    fields = ['pts', 'reb', 'ast', 'stl', 'blk', 'turnover', 'pf', 'fgm', 'games_played', 'fga', 'fg3m', 'fg3a', 'ftm', 'fta', 'oreb', 'dreb', 'fg_pct', 'fg3_pct', 'ft_pct']

    # Select the fields to filter for
    selected_fields = st.sidebar.multiselect('Select fields to filter for:', options=fields, default=['games_played', 'pts', 'reb', 'ast'])
    selected_year = st.sidebar.selectbox('Select year:', options=forYear)

    stats_df = stats_df[stats_df['season'] == int(selected_year)]

    # Create sliders for the selected fields and filter the DataFrame
    for field in selected_fields:
        min_value = int(stats_df[field].min()) if field not in ['fg_pct', 'fg3_pct', 'ft_pct'] else math.floor(stats_df[field].min() * 100)
        max_value = math.ceil(stats_df[field].max()) if field not in ['fg_pct', 'fg3_pct', 'ft_pct'] else math.ceil(stats_df[field].max() * 100)

        field_range = st.sidebar.slider(f"Filter by {field} range:", min_value=min_value, max_value=max_value, value=(min_value, max_value), step=1)

        if field in ['fg_pct', 'fg3_pct', 'ft_pct']:
            stats_df = stats_df[(stats_df[field] >= field_range[0] / 100) & (stats_df[field] <= field_range[1] / 100)]
        else:
            stats_df = stats_df[(stats_df[field] >= field_range[0]) & (stats_df[field] <= field_range[1])]

    # Add player names to the DataFrame
    # Add player names and team names to the DataFrame
    stats_df['player_name'] = stats_df['player_id'].apply(lambda x: player_id_to_name.get(x, 'Unknown'))
    stats_df['team_name'] = stats_df['player_id'].apply(lambda x: player_id_to_team.get(x, 'Unknown'))

    # Display the filtered players, their team names, and their selected stats with percentage values multiplied by 100
    for index, row in stats_df.iterrows():
        expander = st.expander(f"Player: {row['player_name']} / {row['team_name']}")
        with expander:
            cols = st.columns(len(selected_fields))
            for i, field in enumerate(selected_fields):
                if field in ['fg_pct', 'fg3_pct', 'ft_pct']:
                    value = row[field] * 100
                else:
                    value = row[field]
                cols[i].metric(field.upper(), value)


if selected == "Home":
    st.header('Description:')
    st.markdown('##')
    st.markdown("StatSphere is a sleek and innovative sports "
                "analytics platform, where fans"
                " can dive into a world of data-driven insights. "
                "Explore your favorite players' performance metrics, "
                "compare their statistics, and uncover hidden patterns"
                " that shape the game. StatSphere is your go-to destination"
                " for in-depth sports analysis, transforming the way you "
                "experience and understand you favorite NBA players.")
    st_lottie(
            bball1,
            speed=1,
            loop=True,
            quality='medium',
            height=300,
            width=None,
            key=None,
            )
    
    st.markdown('---')
elif selected == "Game Viewer":
    gameViewer()
elif selected == "Era Showdown":
    era_compare()
elif selected == "Performance Visualizer":
    playerChart()
elif selected == "Stat Stars":
    seasonAverageFilter()


with st.sidebar:
    st.markdown('---')
    st.write("Send Me Feedback")


contact_form = """
<form action="https://formsubmit.co/ineedapyt@gmail.com" method="POST">
    <input type ="hidden" name="_captcha" value="false">
    <input type ="text" name="name" placeholder="Your Name" required>
    <input type ="email" name="email" placeholder="your email" required>
    <textarea name ="message" placeholder="Your message here" required></textarea>
    <button type ="submit">Send</button>
</form>
"""

st.sidebar.markdown(contact_form, unsafe_allow_html=True)