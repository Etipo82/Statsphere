import requests
import os
import json
import time
import pandas as pd
import sqlite3

baseUrl = 'https://www.balldontlie.io/api/v1/'
playerSearch = 'players/?search='
allPlayers = 'players'
getStats = 'stats'
getTeam = 'teams'
seasonAverages = 'season_averages'
games = 'games'

CACHE_FILE = 'player_cache.json'
SEASON_AVERAGES_CACHE_FILE = 'season_averages_cache.json'
TEAM_CACHE_FILE = 'team.json'

# Load the cached data if it exists
if os.path.exists(CACHE_FILE):
    with open(CACHE_FILE, 'r') as f:
        all_players = json.load(f)


def fetch_teams():
    conn = sqlite3.connect('nba_data.db')
    c = conn.cursor()

    # Check if the teams table is empty
    c.execute('SELECT COUNT(*) FROM teams')
    is_empty = c.fetchone()[0] == 0

    # If the table is empty, fetch the data from the API and insert it into the SQLite database
    if is_empty:
        with open('teams.json', 'r') as f:
            data = json.load(f)["data"]
        
        for team in data:
            c.execute('''
                INSERT INTO teams (id, abbreviation, city, conference, division, full_name, name)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (team["id"], team["abbreviation"], team["city"], team["conference"], team["division"], team["full_name"], team["name"]))

        conn.commit()

    # Retrieve and return the team data from the SQLite database
    c.execute('SELECT full_name, id FROM teams')
    teams_data = {team[0]: team[1] for team in c.fetchall()}

    conn.close()

    return teams_data


def populate_players_from_cache():
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, 'r') as f:
            all_players = json.load(f)
        
        conn = sqlite3.connect('nba_data.db')
        c = conn.cursor()

        for player in all_players:
            c.execute('''
                INSERT OR IGNORE INTO players (id, first_name, last_name, full_name, team_id, team_name)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (player["id"], player["first_name"], player["last_name"], f'{player["first_name"]} {player["last_name"]}', 
                  player["team"]["id"], player["team"]["full_name"]))

        conn.commit()
        conn.close()
    else:
        print("CACHE_FILE not found. Please ensure the file exists.")


def create_db():
    conn = sqlite3.connect('nba_data.db')
    c = conn.cursor()

    c.execute('''
        CREATE TABLE IF NOT EXISTS players (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            full_name TEXT,
            team_id INTEGER,
            team_name TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS teams (
            id INTEGER PRIMARY KEY,
            abbreviation TEXT,
            city TEXT,
            conference TEXT,
            division TEXT,
            full_name TEXT,
            name TEXT
        )
    ''')

    c.execute('''
        CREATE TABLE IF NOT EXISTS season_stats (
            id INTEGER PRIMARY KEY,
            player_id INTEGER,
            season INTEGER,
            pts REAL,
            reb REAL,
            ast REAL,
            stl REAL,
            blk REAL,
            turnover REAL,
            pf REAL,
            fgm REAL,
            games_played INTEGER,
            fga REAL,
            fg3m REAL,
            fg3a REAL,
            ftm REAL,
            fta REAL,
            oreb REAL,
            dreb REAL,
            fg_pct REAL,
            fg3_pct REAL,
            ft_pct REAL,
            FOREIGN KEY (player_id) REFERENCES players (id)
        )
    ''')

    conn.commit()
    conn.close()


def fetch_season_averages(current_season):
    player_ids = [player['id'] for player in all_players]
    season_averages = []

    players_per_request = 45
    cooldown_seconds = 1 * 60  # 1 minutes

    conn = sqlite3.connect('nba_data.db')
    c = conn.cursor()

    for i in range(0, len(player_ids), players_per_request):
        batch_player_ids = player_ids[i:i + players_per_request]
        
        for player_id in batch_player_ids:
            url =(f'{baseUrl}{seasonAverages}?season={current_season}&player_ids[]={player_id}')
            response = requests.get(url)
            print(url)
            data = response.json()
            log = open("API_Request_log.txt", "a")
            log.write(f"[GET]:{url} - {response}")

            
            # Only add players who have played at least one game and the season matches the current season
            if data['data'] and data['data'][0]['games_played'] > 0:
                season_stat = data['data'][0]

                # Insert the season stats into the SQLite database
                c.execute('''
                    INSERT OR IGNORE INTO season_stats (player_id, season, pts, reb, ast, stl, blk, turnover, pf, fgm, games_played, fga, fg3m, fg3a, ftm, fta, oreb, dreb, fg_pct, fg3_pct, ft_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (season_stat['player_id'], current_season, season_stat['pts'], season_stat['reb'], season_stat['ast'], season_stat['stl'], season_stat['blk'], season_stat['turnover'], season_stat['pf'], season_stat['fgm'], season_stat['games_played'], season_stat['fga'], season_stat['fg3m'], season_stat['fg3a'], season_stat['ftm'], season_stat['fta'], season_stat['oreb'], season_stat['dreb'], season_stat['fg_pct'], season_stat['fg3_pct'], season_stat['ft_pct']))
                conn.commit()

                season_averages.append(season_stat)
        
        if i + players_per_request < len(player_ids):
            print(f"Waiting for {cooldown_seconds / 60} minutes before the next batch of requests.")
            time.sleep(cooldown_seconds)

    conn.close()


def fetch_season_averages_from_cache(current_season):
    # Load the cached data if it exists
    if os.path.exists(SEASON_AVERAGES_CACHE_FILE):
        with open(SEASON_AVERAGES_CACHE_FILE, 'r') as f:
            cached_data = json.load(f)
            print("First few records in the cache file:", cached_data[:5])

        conn = sqlite3.connect('nba_data.db')
        c = conn.cursor()

        for season_stat in cached_data:
            print("Processing season_stat:", season_stat)
            # Only add players who have played at least one game and the season matches the current season
            if season_stat['games_played'] > 0:
                # Insert the season stats into the SQLite database
                c.execute('''
                    INSERT OR IGNORE INTO season_stats (player_id, season, pts, reb, ast, stl, blk, turnover, pf, fgm, games_played, fga, fg3m, fg3a, ftm, fta, oreb, dreb, fg_pct, fg3_pct, ft_pct)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (season_stat['player_id'], current_season, season_stat['pts'], season_stat['reb'], season_stat['ast'], season_stat['stl'], season_stat['blk'], season_stat['turnover'], season_stat['pf'], season_stat['fgm'], season_stat['games_played'], season_stat['fga'], season_stat['fg3m'], season_stat['fg3a'], season_stat['ftm'], season_stat['fta'], season_stat['oreb'], season_stat['dreb'], season_stat['fg_pct'], season_stat['fg3_pct'], season_stat['ft_pct']))
                print(f"Inserted season stat for player {season_stat['player_id']} and season {current_season}")
                conn.commit()

        # Fetch all records from the season_stats table and print them
        c.execute("SELECT * FROM season_stats")
        fetched_data = c.fetchall()
        print("Data in the season_stats table:", fetched_data)

        conn.close()
    else:
        print("Season averages cache file not found.")


def insert_player(player_id, first_name, last_name, full_name, team_id, team_name):
    conn = sqlite3.connect('nba_data.db')
    c = conn.cursor()

    c.execute('''
        INSERT OR IGNORE INTO players (id, first_name, last_name, full_name, team_id, team_name)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (player_id, first_name, last_name, full_name, team_id, team_name))

    conn.commit()
    conn.close()


def get_all_players():
    conn = sqlite3.connect('nba_data.db')
    c = conn.cursor()

    c.execute('SELECT * FROM players')
    players = c.fetchall()

    conn.close()

    return players


def get_player_season_stats(player_id, season):
    conn = sqlite3.connect('nba_data.db')
    c = conn.cursor()

    c.execute('SELECT * FROM season_stats WHERE player_id = ? AND season = ?', (player_id, season))
    stats = c.fetchone()

    conn.close()

    return stats


def manage_database():
    while True:
        print("\nChoose an action:")
        print("1. Insert a player")
        print("2. View all players")
        print("3. View a player's season stats")
        print("4. Exit")

        action = int(input("Enter the number of your chosen action: "))

        if action == 1:
            player_id = int(input("Enter the player ID: "))
            first_name = input("Enter the player's first name: ")
            last_name = input("Enter the player's last name: ")
            full_name = input("Enter the player's full name: ")

            insert_player(player_id, first_name, last_name, full_name)

        elif action == 2:
            players = get_all_players()
            print("\nAll Players:")
            for player in players:
                print(f"{player[0]}: {player[1]} {player[2]} ({player[3]})")

        elif action == 3:
            player_id = int(input("Enter the player ID: "))
            season = int(input("Enter the season: "))

            stats = get_player_season_stats(player_id, season)
            if stats:
                print(f"\n{stats[1]} season stats for player {stats[2]}:")
                print(f"Points: {stats[3]}, Rebounds: {stats[4]}, Assists: {stats[5]}, Steals: {stats[6]}, Blocks: {stats[7]}, Turnovers: {stats[8]}, Personal Fouls: {stats[9]}, Field Goals Made: {stats[10]}, Games Played: {stats[11]}, Field Goals Attempted: {stats[12]}, 3-Point Field Goals Made: {stats[13]}, 3-Point Field Goals Attempted: {stats[14]}, Free Throws Made: {stats[15]}, Free Throws Attempted: {stats[16]}, Offensive Rebounds: {stats[17]}, Defensive Rebounds: {stats[18]}, Field Goal Percentage: {stats[19]}, 3-Point Field Goal Percentage: {stats[20]}, Free Throw Percentage: {stats[21]}")
            else:
                print("No stats found for this player and season.")

        elif action == 4:
            break

        else:
            print("Invalid input. Please try again.")

# (Previous imports and function definitions)
def main():
    while True:
        print("\nMain Menu:")
        print("1. Create Database")
        print("2. Fetch Season Averages")
        print("3. Manage Database")
        print("4. Fetch Teams")
        print("5. Populate Players from Cache")
        print("6. Fetch Season Averages From Cache")
        print("7. Exit")

        choice = int(input("Enter the number of your chosen action: "))

        if choice == 1:
            create_db()
            print("Database created successfully.")

        elif choice == 2:
            current_season = input('Enter season (Example, to retrieve 2015 season, Enter: 2014): ')  # Update this value according to the current season
            fetch_season_averages(current_season)

            with open(SEASON_AVERAGES_CACHE_FILE, 'r') as f:
                cached_data = json.load(f)

            stats_df = pd.DataFrame(cached_data)
            print(stats_df.head())

        elif choice == 3:
            manage_database()

        elif choice == 4:
            fetch_teams()
            print("Teams fetched and added to the database successfully.")

        elif choice == 5:
            populate_players_from_cache()
            print("Players populated from cache successfully.")

        elif choice == 6:
            current_season = '2022'
            fetch_season_averages_from_cache(current_season)
            print("Season Stats fetched and added to the database successfully.")

        elif choice == 7:
            print("Exiting the application.")
            break

        else:
            print("Invalid input. Please try again.")



if __name__ == "__main__":
    main()
