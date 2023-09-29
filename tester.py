#notes: games with zach are games he played more than half the game. so this years bills game counts for him, and the patriots blowout in 2021 does not count for him, where he left with 12:37 to go in 2nd quarter down 17-0 after going 6/10 for 51 yards. maike white would go 20/32 for 202 1td/2int and they lose 54-13
#for all opponent season average statistics, I exempted their jets games from the stats. so the stats listed are season averages against all teams except the jets
#total points for and against do not include return tds. manually include those. for and against each season
#TODO: edit to include all team stats. why not. is there any way to get passing stats? if not ignore it. choose subset of most compelling stats. as many insteresting ones as possible without cherry picking. and present it in a pretty way

#TODO: prioritize loading of qbs who are starters, in afc, and/or got playing time. put those in order and get as many as possible

from pro_football_reference_web_scraper import player_game_log as p
from pro_football_reference_web_scraper import team_game_log as t
import pickle
import os
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'
pd.set_option('display.float_format', lambda x: f'{x:.4g}')
import time
from tabulate import tabulate
import re
from datetime import datetime



#global variables
# PWD = '/Users/andrewbaird/Desktop/pro_football_scraper'
PWD = '~'
REFRESH_DATA = False
ZACH_WEEKS = {
    2021: {'zach':[1,2,3,4,5,12,13,14,15,16,17,18], 'no_zach':[7,8,9,10,11]},
    2022: {'zach':[4,5,6,7,8,9,11,15,16], 'no_zach':[1,2,3,12,13,14,17,18]},
    2023: {'zach':[1,2,3], 'no_zach':[]},
    }
VALUE_MAPPING = {'W': 1.0, 'L': 0.0, 'T':0.5}

columns_to_keep = ['week', 'opp', 'result', 'points_for', 'points_allowed', 'tot_yds', 'pass_yds', 'rush_yds', 'opp_tot_yds', 'opp_pass_yds', 'opp_rush_yds']
qb_stats = ["cmp", "att", "pass_yds", "pass_td", "int", "rating", "sacked", "rush_att", "rush_yds", "rush_td", "comp_percent", "yd_att", "td_percent", "int_percent"]


QB_list_2022 = {
 'Arizona Cardinals': ['Kyler Murray', 'Colt McCoy', 'David Blough', 'Trace McSorley'],
 'Atlanta Falcons': ['Marcus Mariota', 'Desmond Ridder'],
 'Baltimore Ravens': ['Lamar Jackson', 'Tyler Huntley', 'Anthony Brown'],
 'Buffalo Bills': ['Josh Allen', 'Case Keenum'],
 'Carolina Panthers': ['Sam Darnold', 'P.J. Walker', 'Jacob Eason', 'Baker Mayfield'],
 'Chicago Bears': ['Justin Fields', 'Trevor Siemian', 'Nathan Peterman', 'Tim Boyle'],
 'Cincinnati Bengals': ['Joe Burrow', 'Brandon Allen'],
 'Cleveland Browns': ['Jacoby Brissett', 'Deshaun Watson'],
 'Dallas Cowboys': ['Dak Prescott', 'Cooper Rush'],
 'Denver Broncos': ['Russell Wilson', 'Brett Rypien'],
 'Detroit Lions': ['Jared Goff'],
 'Green Bay Packers': ['Aaron Rodgers', 'Jordan Love'],
 'Houston Texans': ['Davis Mills', 'Kyle Allen', 'Jeff Driskel'],
 'Indianapolis Colts': ['Matt Ryan', 'Sam Ehlinger', 'Nick Foles'],
 'Jacksonville Jaguars': ['Trevor Lawrence', 'CJ Beathard'],
 'Kansas City Chiefs': ['Patrick Mahomes', 'Chad Henne'],
 'Las Vegas Raiders': ['Derek Carr', 'Jarrett Stidham'],
 'Los Angeles Chargers': ['Justin Herbert', 'Chase Daniel'],
 'Los Angeles Rams': ['Matthew Stafford', 'John Wolford', 'Bryce Perkins', 'Baker Mayfield'],
 'Miami Dolphins': ['Tua Tagovailoa', 'Teddy Bridgewater', 'Skylar Thompson'],
 'Minnesota Vikings': ['Kirk Cousins', 'Nick Mullens'],
 'New England Patriots': ['Mac Jones', 'Bailey Zappe', 'Brian Hoyer'],
 'New Orleans Saints': ['Andy Dalton', 'Jameis Winston'],
 'New York Giants': ['Daniel Jones', 'Davis Webb', 'Tyrod Taylor'],
 'New York Jets': ['Mike White', 'Joe Flacco', 'Zach Wilson', 'Chris Streveler'],
 'Philadelphia Eagles': ['Jalen Hurts', 'Gardner Minshew'],
 'Pittsburgh Steelers': ['Kenny Pickett', 'Mitchell Trubisky'],
 'San Francisco 49ers': ['Brock Purdy', 'Trey Lance', 'Josh Johnson', 'Jimmy Garoppolo'],
 'Seattle Seahawks': ['Geno Smith'],
 'Tampa Bay Buccaneers': ['Tom Brady', 'Blaine Gabbert', 'Kyle Trask'],
 'Tennessee Titans': ['Ryan Tannehill', 'Joshua Dobbs', 'Malik Willis'],
 'Washington Commanders': ['Taylor Heinicke', 'Carson Wentz', 'Sam Howell'],
#  'Washington Football Team': ['Taylor Heinicke', 'Carson Wentz', 'Sam Howell'],
#  'Washington Redskins': ['Taylor Heinicke', 'Carson Wentz', 'Sam Howell'],
}

# abrevs = ['ARI', 'ATL', 'BAL', 'BUF', 'CAR', 'CHI', 'CIN', 'CLE', 'DAL', 'DEN', 'DET', 'GNB', 'HOU', 'IND', 'JAX', 'KAN', 'LAC', 'LAR', 'LVR', 'MIA', 'MIN', 'NOR', 'NWE', 'NYG', 'NYJ', 'PHI', 'PIT', 'SEA', 'SFO', 'TAM', 'TEN', 'WAS']
franchise_abbreviations = {
    # "Arizona Cardinals": {"Official Team Abbreviation": "ARZ", "Commonly Used Abbreviation": "ARI"},
    "Arizona Cardinals": {"Official Team Abbreviation": "ARI", "Commonly Used Abbreviation": "ARI"},
    "Atlanta Falcons": {"Official Team Abbreviation": "ATL", "Commonly Used Abbreviation": "ATL"},
    # "Baltimore Ravens": {"Official Team Abbreviation": "BLT", "Commonly Used Abbreviation": "BAL"},
    "Baltimore Ravens": {"Official Team Abbreviation": "BAL", "Commonly Used Abbreviation": "BAL"},
    "Buffalo Bills": {"Official Team Abbreviation": "BUF", "Commonly Used Abbreviation": "BUF"},
    "Carolina Panthers": {"Official Team Abbreviation": "CAR", "Commonly Used Abbreviation": "CAR"},
    "Chicago Bears": {"Official Team Abbreviation": "CHI", "Commonly Used Abbreviation": "CHI"},
    "Cincinnati Bengals": {"Official Team Abbreviation": "CIN", "Commonly Used Abbreviation": "CIN"},
    # "Cleveland Browns": {"Official Team Abbreviation": "CLV", "Commonly Used Abbreviation": "CLE"},
    "Cleveland Browns": {"Official Team Abbreviation": "CLE", "Commonly Used Abbreviation": "CLE"},
    "Dallas Cowboys": {"Official Team Abbreviation": "DAL", "Commonly Used Abbreviation": "DAL"},
    "Denver Broncos": {"Official Team Abbreviation": "DEN", "Commonly Used Abbreviation": "DEN"},
    "Detroit Lions": {"Official Team Abbreviation": "DET", "Commonly Used Abbreviation": "DET"},
    "Green Bay Packers": {"Official Team Abbreviation": "GNB", "Commonly Used Abbreviation": "GNB"},
    # "Houston Texans": {"Official Team Abbreviation": "HST", "Commonly Used Abbreviation": "HOU"},
    "Houston Texans": {"Official Team Abbreviation": "HOU", "Commonly Used Abbreviation": "HOU"},
    "Indianapolis Colts": {"Official Team Abbreviation": "IND", "Commonly Used Abbreviation": "IND"},
    "Jacksonville Jaguars": {"Official Team Abbreviation": "JAX", "Commonly Used Abbreviation": "JAC"},
    # "Kansas City Chiefs": {"Official Team Abbreviation": "KC", "Commonly Used Abbreviation": "KC"},
    "Kansas City Chiefs": {"Official Team Abbreviation": "KAN", "Commonly Used Abbreviation": "KC"},
    # "Las Vegas Raiders": {"Official Team Abbreviation": "LV", "Commonly Used Abbreviation": "LV"},
    "Las Vegas Raiders": {"Official Team Abbreviation": "LVR", "Commonly Used Abbreviation": "LV"},
    "Los Angeles Chargers": {"Official Team Abbreviation": "LAC", "Commonly Used Abbreviation": "LAC"},
    "Los Angeles Rams": {"Official Team Abbreviation": "LAR", "Commonly Used Abbreviation": "LAR"},
    "Miami Dolphins": {"Official Team Abbreviation": "MIA", "Commonly Used Abbreviation": "MIA"},
    "Minnesota Vikings": {"Official Team Abbreviation": "MIN", "Commonly Used Abbreviation": "MIN"},
    "New England Patriots": {"Official Team Abbreviation": "NWE", "Commonly Used Abbreviation": "NWE"},
    "New Orleans Saints": {"Official Team Abbreviation": "NO", "Commonly Used Abbreviation": "NO"},
    "New York Giants": {"Official Team Abbreviation": "NYG", "Commonly Used Abbreviation": "NYG"},
    "New York Jets": {"Official Team Abbreviation": "NYJ", "Commonly Used Abbreviation": "NYJ"},
    "Philadelphia Eagles": {"Official Team Abbreviation": "PHI", "Commonly Used Abbreviation": "PHI"},
    "Pittsburgh Steelers": {"Official Team Abbreviation": "PIT", "Commonly Used Abbreviation": "PIT"},
    # "San Francisco 49ers": {"Official Team Abbreviation": "SF", "Commonly Used Abbreviation": "SF"},
    "San Francisco 49ers": {"Official Team Abbreviation": "SFO", "Commonly Used Abbreviation": "SF"},
    "Seattle Seahawks": {"Official Team Abbreviation": "SEA", "Commonly Used Abbreviation": "SEA"},
    "Tampa Bay Buccaneers": {"Official Team Abbreviation": "TAM", "Commonly Used Abbreviation": "TB"},
    "Tennessee Titans": {"Official Team Abbreviation": "TEN", "Commonly Used Abbreviation": "TEN"},
    "Washington Commanders": {"Official Team Abbreviation": "WAS", "Commonly Used Abbreviation": "WAS"},
}


def get_all_qb_games_vs_team(team_game_log, team_name= "Buffalo Bills",season=2022, holdout=["New York Jets", "NYJ"]):
    opposing_qb_df = pd.DataFrame(columns=['QB', 'date', 'week', 'team', 'game_location', 'opp', 'result', 'team_pts', 'opp_pts', 'cmp', 'att', 'pass_yds', 'pass_td', 'int', 'rating', 'sacked', 'rush_att', 'rush_yds', 'rush_td'])
    
    quarterbacks_already_looped_through = []
    for index, row in team_game_log.iterrows():
        week = row['week']
        opp = row['opp']
        if not opp in holdout:
            # print(f"opp {opp} not in holdout list {holdout}")
            try:
                for quarterback in QB_list_2022[opp]:
                    if not quarterback in quarterbacks_already_looped_through:
                        # print(f"week {week} opp {opp} quarterback {quarterback}")
                        qb_df, _, _, _ = get_player_data(player=quarterback, position="QB", season=season, refresh_data=False)
                        # print(f"df {qb_df} {franchise_abbreviations[team_name]['Official Team Abbreviation']}")
                        qb_df = qb_df[qb_df['opp'].isin([franchise_abbreviations[team_name]["Official Team Abbreviation"]])]
                        # qb_df['QB']=quarterback
                        qb_df.insert(0, 'QB', quarterback)
                        # print(f"df filtered {qb_df}")

                        if not qb_df.empty:
                            if not opposing_qb_df.empty:
                                opposing_qb_df = pd.concat([opposing_qb_df, qb_df], ignore_index=True)
                            else:
                                opposing_qb_df = qb_df

                        quarterbacks_already_looped_through.append(quarterback)

            except:
                pass

    opposing_qb_df = opposing_qb_df.sort_values('week')

    for index, row in opposing_qb_df.iterrows():
        comp = row['cmp']
        att = row['att']
        yds = row['pass_yds']
        td = row['pass_td']
        ints = row['int']
        if att > 0:
            opposing_qb_df.loc[index, 'rating'] = passer_rating(comp = comp, att=att, yds=yds, td=td, ints=ints)
            opposing_qb_df.loc[index, 'comp_percent'] = comp/att*100
            opposing_qb_df.loc[index, 'yd_att'] = yds/att
            opposing_qb_df.loc[index, 'td_percent'] = td/att*100
            opposing_qb_df.loc[index, 'int_percent'] = ints/att*100
        else:
            opposing_qb_df.loc[index, 'rating'] = 0.0
            opposing_qb_df.loc[index, 'comp_percent'] = 0.0
            opposing_qb_df.loc[index, 'yd_att'] = 0.0
            opposing_qb_df.loc[index, 'td_percent'] = 0.0
            opposing_qb_df.loc[index, 'int_percent'] = 0.0

    return opposing_qb_df

    
def passer_rating(comp, att, yds, td, ints):
    if att > 0:
        a = (comp/att - 0.3)*5
        a = max(0, min(2.375, a))
        b = (yds/att - 3)*0.25
        b = max(0, min(2.375, b))
        c = (td/att)*20
        c = max(0, min(2.375, c))
        d = 2.375 - ((ints/att)*25)
        d = max(0, min(2.375, d))
        rating = ((a+b+c+d)/6)*100
    else:
        rating = 0.0
    return rating


def get_qb_avg_stats(opposing_qb_df):
    # means = opposing_qb_df.iloc[:, 8:].mean()
    number_of_games = opposing_qb_df['week'].nunique()
    if number_of_games > 0:
        means = opposing_qb_df.iloc[:, 9:].sum()/number_of_games
    else:
        means = opposing_qb_df.iloc[:, 9:].sum()
    means_df = pd.DataFrame(means).transpose()
    comp = means_df.iloc[0, 0]
    att = means_df.iloc[0, 1]
    yds = means_df.iloc[0, 2]
    td = means_df.iloc[0, 3]
    ints = means_df.iloc[0, 4]
    rating_cumulative = passer_rating(comp = comp, att=att, yds=yds, td=td, ints=ints)
    # means_df.insert(10, 'rating_cumulative', rating_cumulative)
    if att > 0:
        means_df['rating'] = rating_cumulative
        means_df['comp_percent'] = comp/att*100
        means_df['yd_att'] = yds/att
        means_df['td_percent'] = td/att*100
        means_df['int_percent'] = ints/att*100
    else:
        means_df['rating'] = 0.0
        means_df['comp_percent'] = 0.0
        means_df['yd_att'] = 0.0
        means_df['td_percent'] = 0.0
        means_df['int_percent'] = 0.0

    # means_df.insert(0, 'wk', 'avgs')
    # means_df.insert(0, 'yr', yearly_dataframe.iloc[0,0])
    # mean_row = pd.DataFrame({'Name': ['Mean'], **means.to_dict()}, index=[0])
    # zach_game_log = pd.concat([zach_game_log, mean_row], ignore_index=True)
    return means_df


#helper functions
def convert_spaces_to_underscores(input_string):
    # Replace spaces with underscores using the `replace()` method
    result = input_string.replace(' ', '_')
    return result

def pickle_path_team(team, season):
    pickle_directory = os.path.join(PWD, 'pickle_files')
    pickle_filename = f'team_gamelog_{convert_spaces_to_underscores(team)}_{season}.pkl'
    return os.path.join(pickle_directory, pickle_filename)

def get_team_data(team, season, refresh_data=False, print_stuff=False):
    if print_stuff:
        print(f'Fetching team data for {team} {season}')
    data_df = None
    pickle_file_path = pickle_path_team(team, season)
    if refresh_data:
        try:
            assert False
            data_df = t.get_team_game_log(team = team, season = season)
            with open(pickle_file_path, 'wb') as file:
                pickle.dump(data_df, file)
        except:
            if os.path.isfile(pickle_file_path):
                if print_stuff:
                    print(f'Unable to load fresh team data for {team} {season}, resorting to saved data.')
                with open(pickle_file_path, 'rb') as file:
                    data_df = pickle.load(file)
            else:
                raise ValueError(f'Unable to load fresh team data OR saved data for {team} {season}.')
    else:
        if os.path.isfile(pickle_file_path):
            with open(pickle_file_path, 'rb') as file:
                data_df = pickle.load(file)
        else:
            try:
                assert False
                data_df = t.get_team_game_log(team = team, season = season)
                with open(pickle_file_path, 'wb') as file:
                    pickle.dump(data_df, file)
            except:
                # raise ValueError(f'Unable to load fresh team data OR saved data for {team} {season}.')
                if print_stuff:
                    print(f'Unable to load fresh team data OR saved data for {team} {season}.')
    if data_df is None:
        data_df = pd.DataFrame(columns=['week', 'day', 'rest_days', 'home_team', 'distance_travelled', 'opp', 'result', 'points_for', 'points_allowed', 'tot_yds', 'pass_yds', 'rush_yds', 'opp_tot_yds', 'opp_pass_yds', 'opp_rush_yds'])
    if print_stuff:
        # print(data_df.columns.tolist())
        print(data_df)
    return data_df

def pickle_path_player(player, position, season):
    pickle_directory = os.path.join(PWD, 'pickle_files')
    pickle_filename = f'player_gamelog_{convert_spaces_to_underscores(player)}_{position}_{season}.pkl'
    return os.path.join(pickle_directory, pickle_filename)

def get_player_data(player, position, season, refresh_data=False, print_stuff=False, send_requests=False):
    data_df = None
    request_sent = False
    player_file_found = False
    if print_stuff:
        print(f'Fetching player data for {player} {position} {season}')
    pickle_file_path = pickle_path_player(player, position, season)
    if refresh_data:
        try:
            assert False
            request_sent = True
            data_df = p.get_player_game_log(player = player, position = position, season = season)
            with open(pickle_file_path, 'wb') as file:
                pickle.dump(data_df, file)
        except:
            if os.path.isfile(pickle_file_path):
                player_file_found = True
                if print_stuff:
                    print(f'Unable to load fresh player data for {player} {position} {season}, resorting to saved data.')
                with open(pickle_file_path, 'rb') as file:
                    data_df = pickle.load(file)
            else:
                # raise ValueError(f'Unable to load fresh player data OR saved data for {player} {position} {season}.')
                if print_stuff:
                    print(f'Unable to load fresh player data OR saved data for {player} {position} {season}.')
    else:
        if os.path.isfile(pickle_file_path):
            player_file_found = True
            with open(pickle_file_path, 'rb') as file:
                data_df = pickle.load(file)
        else:
            try:
                assert False
                request_sent = True
                data_df = p.get_player_game_log(player = player, position = position, season = season)
                with open(pickle_file_path, 'wb') as file:
                    pickle.dump(data_df, file)
            except:
                # raise ValueError(f'Unable to load fresh player data OR saved data for {player} {position} {season}.')
                if print_stuff:
                    print(f'Unable to load fresh player data OR saved data for {player} {position} {season}.')
    if data_df is None:
        data_df = pd.DataFrame(columns=['date', 'week', 'team', 'game_location', 'opp', 'result', 'team_pts', 'opp_pts', 'cmp', 'att', 'pass_yds', 'pass_td', 'int', 'rating', 'sacked', 'rush_att', 'rush_yds', 'rush_td'])
    # if print_stuff:
    #     print(data_df.columns.tolist())

    abbrevs = []
    for index, row in data_df.iterrows():
        if not row['team'] in abbrevs:
            abbrevs.append(row['team'])
        if not row['opp'] in abbrevs:
            abbrevs.append(row['opp'])

    # print(data_df.columns)
    # assert False
    # cols = ['week', 'team_pts',
    #    'opp_pts', 'cmp', 'att', 'pass_yds', 'pass_td', 'int', 
    #    'sacked', 'rush_att', 'rush_yds', 'rush_td']
    cols = ['team_pts', 'week',
       'opp_pts', 'cmp', 'att', 'pass_yds', 'pass_td', 'int', 
       'sacked', 'rush_att', 'rush_yds', 'rush_td']
    for col in cols:
        data_df[col] = data_df[col].astype(int)
    cols = ['date', 'team', 'game_location', 'opp', 'result']
    for col in cols:
        data_df[col] = data_df[col].astype(str)
    cols = ['rating',]
    for col in cols:
        data_df[col] = data_df[col].astype(float)



    return data_df, request_sent, player_file_found, abbrevs
    

def combine_weekly_stats(df):
    # Group by 'week' and aggregate columns accordingly
    aggregated_df = df.groupby('week').agg({
        'QB': lambda x: 'multiple' if len(x) > 1 else x.iloc[0],
        'date': 'first',
        'team': 'first',
        'game_location': 'first',
        'opp': 'first',
        'result': 'first',
        'team_pts': 'first',
        'opp_pts': 'first',
        'cmp': 'sum',
        'att': 'sum',
        'pass_yds': 'sum',
        'pass_td': 'sum',
        'int': 'sum',
        'rating': 'mean',
        'sacked': 'sum',
        'rush_att': 'sum',
        'rush_yds': 'sum',
        'rush_td': 'sum'
    }).reset_index()

    return aggregated_df
    

def generate_jets_qb_stats(season=2022, refresh_data=False):
    jets_qb_df = pd.DataFrame(columns=['QB', 'date', 'week', 'team', 'game_location', 'opp', 'result', 'team_pts', 'opp_pts', 'cmp', 'att', 'pass_yds', 'pass_td', 'int', 'rating', 'sacked', 'rush_att', 'rush_yds', 'rush_td'])
    team_game_log = get_team_data(team = "New York Jets", season = season, refresh_data=refresh_data)
    quarterbacks_already_looped_through = []
    for index, row in team_game_log.iterrows():
        week = row['week']
        for quarterback in QB_list_2022["New York Jets"]:
            if not quarterback in quarterbacks_already_looped_through:
                qb_df, _ , _, _= get_player_data(player=quarterback, position="QB", season=season, refresh_data=refresh_data)
                # qb_df['QB']=quarterback
                # print('qb_df', qb_df)
                qb_df.insert(0, 'QB', quarterback)
                if not qb_df.empty:
                    if not jets_qb_df.empty:
                        jets_qb_df = pd.concat([jets_qb_df, qb_df], ignore_index=True)
                    else:
                        jets_qb_df = qb_df

                quarterbacks_already_looped_through.append(quarterback)
        
    jets_qb_df = jets_qb_df.sort_values('week')
    # zach_qb_df = jets_qb_df[jets_qb_df['QB'].isin(ZACH_WEEKS[season]['zach'])]
    zach_qb_df = jets_qb_df[jets_qb_df['QB'] == 'Zach Wilson']
    # nonzach_qb_df = jets_qb_df[jets_qb_df['QB'].isin(ZACH_WEEKS[season]['no_zach'])]
    nonzach_qb_df = jets_qb_df[jets_qb_df['QB'] != 'Zach Wilson']
    nonzach_qb_df = combine_weekly_stats(nonzach_qb_df)

    for index, row in jets_qb_df.iterrows():
        comp = row['cmp']
        att = row['att']
        yds = row['pass_yds']
        td = row['pass_td']
        ints = row['int']
        if att > 0:
            jets_qb_df.loc[index, 'rating'] = passer_rating(comp = comp, att=att, yds=yds, td=td, ints=ints)
            jets_qb_df.loc[index, 'comp_percent'] = comp/att*100
            jets_qb_df.loc[index, 'yd_att'] = yds/att
            jets_qb_df.loc[index, 'td_percent'] = td/att*100
            jets_qb_df.loc[index, 'int_percent'] = ints/att*100
        else:
            jets_qb_df.loc[index, 'rating'] = 0.0
            jets_qb_df.loc[index, 'comp_percent'] = 0.0
            jets_qb_df.loc[index, 'yd_att'] = 0.0
            jets_qb_df.loc[index, 'td_percent'] = 0.0
            jets_qb_df.loc[index, 'int_percent'] = 0.0

    for index, row in zach_qb_df.iterrows():
        comp = row['cmp']
        att = row['att']
        yds = row['pass_yds']
        td = row['pass_td']
        ints = row['int']
        if att > 0:
            zach_qb_df.loc[index, 'rating'] = passer_rating(comp = comp, att=att, yds=yds, td=td, ints=ints)
            zach_qb_df.loc[index, 'comp_percent'] = comp/att*100
            zach_qb_df.loc[index, 'yd_att'] = yds/att
            zach_qb_df.loc[index, 'td_percent'] = td/att*100
            zach_qb_df.loc[index, 'int_percent'] = ints/att*100
        else:
            zach_qb_df.loc[index, 'rating'] = 0.0
            zach_qb_df.loc[index, 'comp_percent'] = 0.0
            zach_qb_df.loc[index, 'yd_att'] = 0.0
            zach_qb_df.loc[index, 'td_percent'] = 0.0
            zach_qb_df.loc[index, 'int_percent'] = 0.0

    for index, row in nonzach_qb_df.iterrows():
        comp = row['cmp']
        att = row['att']
        yds = row['pass_yds']
        td = row['pass_td']
        ints = row['int']
        if att > 0:
            nonzach_qb_df.loc[index, 'rating'] = passer_rating(comp = comp, att=att, yds=yds, td=td, ints=ints)
            nonzach_qb_df.loc[index, 'comp_percent'] = comp/att*100
            nonzach_qb_df.loc[index, 'yd_att'] = yds/att
            nonzach_qb_df.loc[index, 'td_percent'] = td/att*100
            nonzach_qb_df.loc[index, 'int_percent'] = ints/att*100
        else:
            nonzach_qb_df.loc[index, 'rating'] = 0.0
            nonzach_qb_df.loc[index, 'comp_percent'] = 0.0
            nonzach_qb_df.loc[index, 'yd_att'] = 0.0
            nonzach_qb_df.loc[index, 'td_percent'] = 0.0
            nonzach_qb_df.loc[index, 'int_percent'] = 0.0

    return jets_qb_df, zach_qb_df, nonzach_qb_df




def generate_yearly_dataframe(season, zach_status):
    # season = 2022

    jets_qb_df, zach_qb_df, nonzach_qb_df = generate_jets_qb_stats()

    if zach_status == 'zach':
        jets_qb_df_of_interest = zach_qb_df
    elif zach_status == 'no_zach':
        jets_qb_df_of_interest = nonzach_qb_df
    else:
        assert False



    # game_log = t.get_team_game_log(team = 'New York Jets', season = season)
    game_log = get_team_data(team = "New York Jets", season = season, refresh_data=REFRESH_DATA)
    game_log = game_log[columns_to_keep]
    game_log['result'] = game_log['result'].replace(VALUE_MAPPING)

    zach_game_log = game_log[game_log['week'].isin(ZACH_WEEKS[season][zach_status])]
    # pretty_table(zach_game_log)
    for index, row in zach_game_log.iterrows():
        # opponent_game_log = t.get_team_game_log(team = row['opp'], season = season)
        opponent_game_log = get_team_data(team = row['opp'], season = season, refresh_data=REFRESH_DATA)
        opponent_game_log = opponent_game_log[columns_to_keep]
        opponent_game_log['result'] = opponent_game_log['result'].replace(VALUE_MAPPING)
        opponent_game_log_non_nyj = opponent_game_log[opponent_game_log['opp'] != 'New York Jets']
        # team_game_log = get_team_data(team = "New York Jets", season = 2022, refresh_data=False)
        opposing_qb_df = get_all_qb_games_vs_team(opponent_game_log_non_nyj, team_name= row['opp'],season=season, holdout=["New York Jets", "NYJ"])
        opposing_qb_df_avgs = get_qb_avg_stats(opposing_qb_df)
        # qb_stats = ["cmp", "att", "pass_yds", "pass_td", "int", "rating", "sacked", "rush_att", "rush_yds", "rush_td", "rating_cumulative"]
        # pretty_table(jets_qb_df_of_interest)
        # print(row)
        jets_qb_row_of_interest = jets_qb_df_of_interest[jets_qb_df_of_interest['week'] == row['week']].iloc[0]
        for stat in qb_stats:
            zach_game_log.loc[index, f'opp_def_qb_{stat}'] = opposing_qb_df_avgs[stat].mean() #can use the mean because its a one row df
            zach_game_log.loc[index, f'jets_qb_{stat}'] = jets_qb_row_of_interest[stat].mean() #can use the mean because its a one row df
        for item in columns_to_keep[2:]:
            mean_val = opponent_game_log_non_nyj[item].mean()
            zach_game_log.loc[index, f'opp_avg_{item}'] = mean_val


    zach_game_log['points_for_over_expected'] = zach_game_log['points_for'] - zach_game_log['opp_avg_points_allowed']
    zach_game_log['points_allowed_over_expected'] = zach_game_log['points_allowed'] - zach_game_log['opp_avg_points_for']
    zach_game_log['tot_yds_over_expected'] = zach_game_log['tot_yds'] - zach_game_log['opp_avg_opp_tot_yds']
    zach_game_log['rush_yds_over_expected'] = zach_game_log['rush_yds'] - zach_game_log['opp_avg_opp_rush_yds']
    zach_game_log['pass_yds_over_expected'] = zach_game_log['pass_yds'] - zach_game_log['opp_avg_opp_pass_yds']
    zach_game_log['opp_tot_yds_over_expected'] = zach_game_log['opp_tot_yds'] - zach_game_log['opp_avg_tot_yds']
    zach_game_log['opp_rush_yds_over_expected'] = zach_game_log['opp_rush_yds'] - zach_game_log['opp_avg_rush_yds']
    zach_game_log['opp_pass_yds_over_expected'] = zach_game_log['opp_pass_yds'] - zach_game_log['opp_avg_pass_yds']
    zach_game_log['win_percent_over_expected'] = zach_game_log['opp_avg_result']*zach_game_log['result'] - (1 - zach_game_log['opp_avg_result'])*(1 - zach_game_log['result'])

    for qb_stat in qb_stats:
        zach_game_log[f'jets_qb_{qb_stat}_over_expected'] = zach_game_log[f'jets_qb_{qb_stat}'] - zach_game_log[f'opp_def_qb_{qb_stat}']
        zach_game_log[f'jets_qb_{qb_stat}_over_expected_percent'] = 100*((zach_game_log[f'jets_qb_{qb_stat}'] - zach_game_log[f'opp_def_qb_{qb_stat}'])/zach_game_log[f'opp_def_qb_{qb_stat}'])

    # desired_order = ['week', 'opp', 'opp_avg_result', 'result', 'win_percent_over_expected', 'points_for', 'opp_avg_points_allowed', 'points_for_over_expected', 'points_allowed', 'opp_avg_points_for', 'points_allowed_over_expected', 'tot_yds', 'opp_avg_opp_tot_yds', 'tot_yds_over_expected', 'opp_tot_yds', 'opp_avg_tot_yds', 'opp_tot_yds_over_expected', 'pass_yds', 'opp_avg_opp_pass_yds', 'pass_yds_over_expected', 'opp_pass_yds', 'opp_avg_pass_yds', 'opp_pass_yds_over_expected', 'rush_yds', 'opp_avg_opp_rush_yds', 'rush_yds_over_expected', 'opp_rush_yds', 'opp_avg_rush_yds', 'opp_rush_yds_over_expected']
    # zach_game_log = zach_game_log[desired_order]

    # zach_game_log = zach_game_log.rename(columns={'week':'wk', 'opp':'opp', 'opp_avg_result':'opp_avg_W/L%', 'result':'W/L', 'win_percent_over_expected':'W/L%_over_exp', 'points_for':'pts', 'opp_avg_points_allowed':'opp_avg_pts_allowed', 'points_for_over_expected':'pts_over_exp', 'points_allowed':'pts_allowed', 'opp_avg_points_for':'opp_avg_pts', 'points_allowed_over_expected':'pts_allowed_over_exp', 'tot_yds':'tot_yds', 'opp_avg_opp_tot_yds':'opp_avg_yds_allowed', 'tot_yds_over_expected':'tot_yds_over_exp', 'opp_tot_yds':'opp_tot_yds', 'opp_avg_tot_yds':'opp_avg_tot_yds', 'opp_tot_yds_over_expected':'opp_tot_yds_over_exp' })
    zach_game_log.insert(0, 'yr', season)

    return zach_game_log


# def generate_avgs_dataframe(yearly_dataframe):
def generate_avgs_dataframe_old(yearly_dataframe):
    means = yearly_dataframe.iloc[:, 3:].mean()
    means_df = pd.DataFrame(means).transpose()
    means_df.insert(0, 'opp', 'avgs')
    means_df.insert(0, 'wk', 'avgs')
    means_df.insert(0, 'yr', yearly_dataframe.iloc[0,0])
    # mean_row = pd.DataFrame({'Name': ['Mean'], **means.to_dict()}, index=[0])
    # zach_game_log = pd.concat([zach_game_log, mean_row], ignore_index=True)
    return means_df


# def generate_sums_dataframe(yearly_dataframe):
def generate_avgs_dataframe(yearly_dataframe):
    number_of_games = yearly_dataframe['week'].nunique()
    sums = yearly_dataframe.iloc[:, 3:].sum()
    sums_df = pd.DataFrame(sums).transpose()
    # means_df.insert(0, 'opp', 'avgs')
    # means_df.insert(0, 'wk', 'avgs')
    # means_df.insert(0, 'yr', yearly_dataframe.iloc[0,0])
    # mean_row = pd.DataFrame({'Name': ['Mean'], **means.to_dict()}, index=[0])
    # zach_game_log = pd.concat([sums_df, mean_row], ignore_index=True)
    sums_df['points_for_over_expected'] = sums_df['points_for'] - sums_df['opp_avg_points_allowed']
    sums_df['points_allowed_over_expected'] = sums_df['points_allowed'] - sums_df['opp_avg_points_for']
    sums_df['tot_yds_over_expected'] = sums_df['tot_yds'] - sums_df['opp_avg_opp_tot_yds']
    sums_df['rush_yds_over_expected'] = sums_df['rush_yds'] - sums_df['opp_avg_opp_rush_yds']
    sums_df['pass_yds_over_expected'] = sums_df['pass_yds'] - sums_df['opp_avg_opp_pass_yds']
    sums_df['opp_tot_yds_over_expected'] = sums_df['opp_tot_yds'] - sums_df['opp_avg_tot_yds']
    sums_df['opp_rush_yds_over_expected'] = sums_df['opp_rush_yds'] - sums_df['opp_avg_rush_yds']
    sums_df['opp_pass_yds_over_expected'] = sums_df['opp_pass_yds'] - sums_df['opp_avg_pass_yds']
    # sums_df['win_percent_over_expected'] = sums_df['opp_avg_result']*sums_df['result'] - (1 - sums_df['opp_avg_result'])*(1 - sums_df['result'])

    comp = sums_df.at[0, f'jets_qb_cmp']
    att = sums_df.at[0, f'jets_qb_att']
    yds = sums_df.at[0, f'jets_qb_pass_yds']
    td = sums_df.at[0, f'jets_qb_pass_td']
    ints = sums_df.at[0, f'jets_qb_int']

    rating_cumulative = passer_rating(comp = comp, att=att, yds=yds, td=td, ints=ints)
    # print(f'comp = {comp}, att={att}, yds={yds}, td={td}, ints={ints}, num_games={number_of_games}, rating_cumulative = {rating_cumulative}')


    comp_opp_def_qb = sums_df.at[0, f'opp_def_qb_cmp']
    att_opp_def_qb = sums_df.at[0, f'opp_def_qb_att']
    yds_opp_def_qb = sums_df.at[0, f'opp_def_qb_pass_yds']
    td_opp_def_qb = sums_df.at[0, f'opp_def_qb_pass_td']
    ints_opp_def_qb = sums_df.at[0, f'opp_def_qb_int']
    rating_cumulative_opp_def_qb = passer_rating(comp = comp_opp_def_qb, att=att_opp_def_qb, yds=yds_opp_def_qb, td=td_opp_def_qb, ints=ints_opp_def_qb)

    means_df = sums_df/number_of_games

    # means_df.insert(10, 'rating_cumulative', rating_cumulative)
    if att > 0:
        means_df.at[0, 'jets_qb_rating'] = rating_cumulative
        means_df.at[0, 'jets_qb_comp_percent'] = comp/att*100
        means_df.at[0, 'jets_qb_yd_att'] = yds/att
        means_df.at[0, 'jets_qb_td_percent'] = td/att*100
        means_df.at[0, 'jets_qb_int_percent'] = ints/att*100
    else:
        means_df.at[0, 'jets_qb_rating'] = 0.0
        means_df.at[0, 'jets_qb_comp_percent'] = 0.0
        means_df.at[0, 'jets_qb_yd_att'] = 0.0
        means_df.at[0, 'jets_qb_td_percent'] = 0.0
        means_df.at[0, 'jets_qb_int_percent'] = 0.0


        # means_df.insert(10, 'rating_cumulative', rating_cumulative)
    if att_opp_def_qb > 0:
        means_df.at[0, 'opp_def_qb_rating'] = rating_cumulative_opp_def_qb
        means_df.at[0, 'opp_def_qb_comp_percent'] = comp_opp_def_qb/att_opp_def_qb*100
        means_df.at[0, 'opp_def_qb_yd_att'] = yds_opp_def_qb/att_opp_def_qb
        means_df.at[0, 'opp_def_qb_td_percent'] = td_opp_def_qb/att_opp_def_qb*100
        means_df.at[0, 'opp_def_qb_int_percent'] = ints_opp_def_qb/att_opp_def_qb*100
    else:
        means_df.at[0, 'opp_def_qb_rating'] = 0.0
        means_df.at[0, 'opp_def_qb_comp_percent'] = 0.0
        means_df.at[0, 'opp_def_qb_yd_att'] = 0.0
        means_df.at[0, 'opp_def_qb_td_percent'] = 0.0
        means_df.at[0, 'opp_def_qb_int_percent'] = 0.0


    for qb_stat in qb_stats:
        means_df[f'jets_qb_{qb_stat}_over_expected'] = means_df[f'jets_qb_{qb_stat}'] - means_df[f'opp_def_qb_{qb_stat}']
        means_df[f'jets_qb_{qb_stat}_over_expected_percent'] = 100*((means_df[f'jets_qb_{qb_stat}'] - means_df[f'opp_def_qb_{qb_stat}'])/means_df[f'opp_def_qb_{qb_stat}'])
    # qb_stats = ["cmp", "att", "pass_yds", "pass_td", "int", "rating", "sacked", "rush_att", "rush_yds", "rush_td", "comp_percent", "yd_att", "td_percent", "int_percent"]

    means_df.insert(0, 'opp', 'avgs')
    means_df.insert(0, 'wk', 'avgs')
    means_df.insert(0, 'yr', yearly_dataframe.iloc[0,0])

    return means_df

def process_manual_player_stats(player = 'Jacoby Brissett'):
    # print('player', player)
    split_names = player.split(' ')
    # input_file=f'/Users/andrewbaird/Desktop/{split_names[0]}_{split_names[1]}.csv'
    input_file=f'~/{split_names[0]}_{split_names[1]}.csv'
    try:
        df = pd.read_csv(input_file)
    except:
        df = pd.read_excel(input_file, engine='xlrd')

    # ['date', 'week', 'team', 'game_location', 'opp', 'result', 'team_pts',
    #    'opp_pts', 'cmp', 'att', 'pass_yds', 'pass_td', 'int', 'rating',
    #    'sacked', 'rush_att', 'rush_yds', 'rush_td']

    # [    'Rk',   'Date',     'G#',   'Week',    'Age',     'Tm',      nan,
    #       'Opp', 'Result',     'GS',    'Cmp',    'Att',   'Cmp%',    'Yds',
    #        'TD',    'Int',   'Rate',     'Sk',    'Yds',    'Y/A',   'AY/A',
    #       'Att',    'Yds',    'Y/A',     'TD',     'TD',    'Pts',     'Sk',
    #      'Solo',    'Ast',   'Comb',    'TFL', 'QBHits',    'Fmb',     'FL',
    #        'FF',     'FR',    'Yds',     'TD',    'Num',    'Pct',    'Num',
    #       'Pct',    'Num',    'Pct', 'Status']

    # Assuming your DataFrame is named df
    # Drop the "Unnamed" columns
    # df = df.loc[:, ~df.columns.str.startswith('Unnamed')]

    # Set the first row as the column headers
    df.iloc[0,18] = 'sack_yds'
    df.iloc[0,19] = 'pass_y/a'
    df.iloc[0,20] = 'pass_any/a'
    df.iloc[0,21] = 'rush_att'
    df.iloc[0,22] = 'rush_yds'
    df.iloc[0,23] = 'rush_yd/att'
    df.iloc[0,24] = 'rush_td'
    for i in range(len(df.columns) - 25):
        df.iloc[0,i+25] = f'col_{i+25}'


    new_header = df.iloc[0]  # Get the first row
    df = df[1:]  # Exclude the first row from the DataFrame
    df = df[:-1]  # Exclude the first row from the DataFrame
    df.columns = new_header  # Set the first row as column headers

    # Reset the index
    df.reset_index(drop=True, inplace=True)
    # pretty_table(df, title='TEST')

    # Now df contains the DataFrame with the desired column headers and without "Unnamed" columns

    # print('skdvjbw', df.columns)
    columns={
        # df.columns[0]: '',
        df.columns[1]: 'date',
        # df.columns[2]: '',
        df.columns[3]: 'week',
        # df.columns[4]: '',
        df.columns[5]: 'team',
        df.columns[6]: 'game_location',
        df.columns[7]: 'opp',
        df.columns[8]: 'result_score',
        # df.columns[9]: '',
        df.columns[10]: 'cmp',
        df.columns[11]: 'att',
        # df.columns[12]: '',
        df.columns[13]: 'pass_yds',
        df.columns[14]: 'pass_td',
        df.columns[15]: 'int',
        df.columns[16]: 'rating',
        df.columns[17]: 'sacked',
        # df.columns[18]: '',
        # df.columns[19]: '',
        # df.columns[20]: '',
        df.columns[21]: 'rush_att',
        df.columns[22]: 'rush_yds',
        # df.columns[23]: '',
        df.columns[24]: 'rush_td',
    }
    df = df.rename(columns=columns)

    # cols2 = {
    #     'Att':'att',
    #     'Yds'
    # }
    # pretty_table(df, title='TEST0')
    # df = df[list(columns.values())]
    # pretty_table(df, title='TEST1')
    df['team_pts'] = None
    df['opp_pts'] = None
    df['result'] = None
    # Split the "result_score" column into three columns
    for index, row in df.iterrows():
        # print(row)
        # print("row['result_score']", row['result_score'])
        stringy_guy = re.split(r'[\s-]', row['result_score'])
        # print(stringy_guy, 'stringy_guy')
        df.at[index, 'result'] = stringy_guy[0]
        df.at[index, 'team_pts'] = int(stringy_guy[1])
        df.at[index, 'opp_pts'] = int(stringy_guy[2])

        # Convert the date string to a datetime object
        date_obj = datetime.strptime(row['date'], '%m/%d/%y')

        # Format the datetime object as 'YYYY-MM-DD'
        formatted_date = date_obj.strftime('%Y-%m-%d')
        df.at[index, 'date'] = formatted_date


        # df[['result', 'team_pts', 'opp_pts']] = 

    # Convert "team_pts" and "opp_pts" to integers
    # df['team_pts'] = df['team_pts'].astype(int)
    # df['opp_pts'] = df['opp_pts'].astype(int)
    # df = df[['Date','Week','Tm','game_location', 'Opp', 'Result',  'Cmp',    'Att',  'Yds','TD',    'Int','Rate',     'Sk',    'Yds',    'Y/A',   'AY/A', 'Att',    'Yds',    'Y/A', 'TD']]
    col_vals = list(columns.values())
    col_vals.insert(5, 'result')
    col_vals.insert(6, 'team_pts')
    col_vals.insert(7, 'opp_pts')
    col_vals.remove('result_score')
    df = df[col_vals]
    df['game_location'] = df['game_location'].fillna('')
    df = df.fillna(0)
    pretty_table(df, title=player)

    pickle_file_path = pickle_path_player(player, position='QB', season=2022)

    with open(pickle_file_path, 'wb') as file:
        pickle.dump(df, file)




def pretty_table(df, title=''):
    comparison_df = df
    numeric_cols = comparison_df.select_dtypes(include='number')
    comparison_df[numeric_cols.columns] = numeric_cols.round(2)

    # # Print the head of the comparison dataframe
    # print(comparison_df.head())

    table = tabulate(comparison_df, headers='keys', tablefmt='pretty')

    # print(comparison_df)
    if title:
        print(title)
    print(table)


def main():

    # df, request_sent, player_file_found, _ = get_player_data(player='Aaron Rodgers', position="QB", season=2022, refresh_data=False, print_stuff=False)
    # # print(df)

    # needed_players = ['Jeff Driskel', 'John Wolford', 'Trace McSorley', 'Tyler Huntley', 'Tyrod Taylor', 'Brian Hoyer', 'Brock Purdy', 'CJ Beathard', 'Chase Daniel', 'Chris Streveler', 'Malik Willis', 'Cooper Rush', 'Gardner Minshew', 'Jacoby Brissett']
    # # needed_players = ['John Wolford', 'Trace McSorley', 'Tyler Huntley', 'Tyrod Taylor', 'Brian Hoyer', 'Brock Purdy', 'CJ Beathard', 'Chase Daniel', 'Chris Streveler', 'Malik Willis', 'Cooper Rush', 'Gardner Minshew', 'Jacoby Brissett']

    # for needed_player in needed_players:
    #     process_manual_player_stats(needed_player)
    # pretty_table(df, title='AROD')
    # assert False



    if 0:
        player_list = []
        i = 0
        for team in QB_list_2022:
            for player in QB_list_2022[team]:
                if player in player_list:
                    pass
                else:
                    i += 1
                    player_list.append(player)
                    # print(f"{i} {player}")
        player_list.sort()




        players_not_found = []
        # nofile_players = ['Gardner Minshew', 'Jacob Eason', 'Jacoby Brissett', 'Jarrett Stidham', 'Jeff Driskel', 'John Wolford', 'Josh Johnson', 'Kyle Trask', 'Kyler Murray', 'Marcus Mariota', 'P.J. Walker', 'Sam Darnold', 'Sam Howell', 'Trace McSorley', 'Trey Lance', 'Tyler Huntley', 'Tyrod Taylor', 'Blaine Gabbert', 'Brian Hoyer', 'Brock Purdy', 'Bryce Perkins', 'CJ Beathard', 'Chad Henne', 'Chase Daniel', 'Chris Streveler', 'Malik Willis', 'Nick Foles', 'Cooper Rush']
        # nofile_players = ['Gardner Minshew', 'Jacob Eason', 'Jacoby Brissett', 'Jarrett Stidham', 'Jeff Driskel', 'John Wolford', 'Josh Johnson', 'Kyle Trask', 'Kyler Murray', 'Sam Howell', 'Trace McSorley', 'Trey Lance', 'Tyler Huntley', 'Tyrod Taylor', 'Blaine Gabbert', 'Brian Hoyer', 'Brock Purdy', 'Bryce Perkins', 'CJ Beathard', 'Chad Henne', 'Chase Daniel', 'Chris Streveler', 'Malik Willis', 'Nick Foles', 'Cooper Rush']
        # needed_players = ['Jeff Driskel', 'John Wolford', 'Trace McSorley', 'Trey Lance', 'Tyler Huntley', 'Tyrod Taylor', 'Brian Hoyer', 'Brock Purdy', 'CJ Beathard', 'Chase Daniel', 'Chris Streveler', 'Malik Willis', 'Cooper Rush', 'Gardner Minshew', 'Jacoby Brissett', ] #'Bryce Perkins' rushing only 'Gardner Minshew II' 'Casey Jarrett Beathard'
        # needed_players = ['Tom Brady', 'Blaine Gabbert', 'Brian Hoyer', 'Brock Purdy', 'Bryce Perkins', 'CJ Beathard', 'Chad Henne', 'Chase Daniel', 'Chris Streveler', 'Cooper Rush', 'Gardner Minshew', 'Jacob Eason', 'Jacoby Brissett', 'Jarrett Stidham', 'Jeff Driskel', 'John Wolford', 'Josh Johnson', 'Kyle Trask', 'Malik Willis', 'Nick Foles', 'Sam Howell', 'Trace McSorley', 'Tyler Huntley', 'Tyrod Taylor', 'Tom Brady']
        # player_list = nofile_players
        # needed_players = ['Jeff Driskel', 'John Wolford', 'Trace McSorley', 'Tyler Huntley', 'Tyrod Taylor', 'Brian Hoyer', 'Brock Purdy', 'CJ Beathard', 'Chase Daniel', 'Chris Streveler', 'Malik Willis', 'Cooper Rush', 'Gardner Minshew', 'Jacoby Brissett']
        # player_list = needed_players
        # player_list = ['Tom Brady', 'Gardner Minshew II']
        abbrevs = []
        for i, player in enumerate(player_list):
            # if player not in nofile_players or 1:
            if 1:
                data, request_sent, player_file_found, abr = get_player_data(player=player, position="QB", season=2022, refresh_data=False, print_stuff=True)
                abbrevs = abbrevs + abr
                print(f'request_sent {request_sent}')
                if request_sent:
                    time.sleep(10)
                    pass
                if not player_file_found:
                    players_not_found.append(player)


        print('abrevs', sorted(list(set(abbrevs))))

        print('players_not_found', players_not_found)

        # team_game_log = get_team_data(team = "New York Jets", season = 2022, refresh_data=False)
        # opposing_qb_df = get_all_qb_games_vs_team(team_game_log, team_name= "New York Jets",season=2022, holdout=["New York Jets", "NYJ"])
        # opposing_qb_df_avgs = get_qb_avg_stats(opposing_qb_df)
        # print(f'opposing_qb_df\n{opposing_qb_df}')
        # print(f'opposing_qb_df_avgs\n{opposing_qb_df_avgs}')


    if 1:

        jets_qb_df, zach_qb_df, nonzach_qb_df = generate_jets_qb_stats()
        pretty_table(jets_qb_df, 'jets_qb_df')
        pretty_table(zach_qb_df, 'zach_qb_df')
        pretty_table(nonzach_qb_df, 'nonzach_qb_df')


        # print(f'jets_qb_df\n{jets_qb_df}')
        # print(f'zach_qb_df\n{zach_qb_df}')
        # print(f'nonzach_qb_df\n{nonzach_qb_df}')

        # print(f'zach_qb_df_avgs\n{get_qb_avg_stats(zach_qb_df)}')
        # print(f'nonzach_qb_df_avgs\n{get_qb_avg_stats(nonzach_qb_df)}')

        # get_team_data(team = "New York Jets", season = 2022, refresh_data=False)
        # get_team_data(team = "New York Jets", season = 2023, refresh_data=False)
        # get_team_data(team = "Kansas City Chiefs", season = 2023, refresh_data=False)
        # for season in [2021, 2022]:
        #     print(f"\nSeason {season} with zach vs without")
        #     zach_game_log = generate_yearly_dataframe(season=season, zach_status='zach')
        #     zach_means = generate_avgs_dataframe(zach_game_log)

        #     # print(f"zach_game_log\n{zach_game_log.to_string(index=False, justify='left')}")
        #     # print(f"zach_means\n{zach_means.to_string(index=False, justify='left')}")
        #     print(zach_means.to_string(index=False, justify='left'))

        #     no_zach_game_log = generate_yearly_dataframe(season=season, zach_status='no_zach')
        #     no_zach_means = generate_avgs_dataframe(no_zach_game_log)

        #     # print(f"no_zach_game_log\n{no_zach_game_log.to_string(index=False, justify='left')}")
        #     # print(f"no_zach_means\n{no_zach_means.to_string(index=False, justify='left')}")
        #     print(no_zach_means.to_string(index=False, justify='left'))

        # combined_df = pd.concat([df1, df2], axis=0)

        # with_zach_2021 = generate_yearly_dataframe(season=2021, zach_status='zach')
        # zach_means_2021 = generate_avgs_dataframe(with_zach_2021)
        with_zach_2022 = generate_yearly_dataframe(season=2022, zach_status='zach')
        zach_means_2022 = generate_avgs_dataframe(with_zach_2022)
        # with_zach_2023 = generate_yearly_dataframe(season=2023, zach_status='zach')
        # zach_means_2023 = generate_avgs_dataframe(with_zach_2023)

        # without_zach_2021 = generate_yearly_dataframe(season=2021, zach_status='no_zach')
        # without_zach_means_2021 = generate_avgs_dataframe(without_zach_2021)
        without_zach_2022 = generate_yearly_dataframe(season=2022, zach_status='no_zach')
        without_zach_means_2022 = generate_avgs_dataframe(without_zach_2022)


        # # with_zach_since_2021 = pd.concat([with_zach_2021, with_zach_2022, with_zach_2023], axis=0)
        # with_zach_since_2021 = pd.concat([with_zach_2021, with_zach_2022], axis=0)
        # with_zach_means_since_2021 = generate_avgs_dataframe(with_zach_since_2021)
        # without_zach_since_2021 = pd.concat([without_zach_2021, without_zach_2022], axis=0)
        # without_zach_means_since_2021 = generate_avgs_dataframe(without_zach_since_2021)

        # with_zach_since_2022 = pd.concat([with_zach_2022, with_zach_2023], axis=0)
        with_zach_since_2022 = pd.concat([with_zach_2022], axis=0)
        with_zach_means_since_2022 = generate_avgs_dataframe(with_zach_since_2022)
        without_zach_since_2022 = without_zach_2022
        without_zach_means_since_2022 = without_zach_means_2022


        # gamelog_column_list = with_zach_since_2022.columns.tolist()
        gamelog_column_list = ['yr', 'week', 'opp', 'result', 'points_for', 'points_allowed', 'tot_yds', 'pass_yds', 'rush_yds', 'opp_tot_yds', 'opp_pass_yds', 'opp_rush_yds', 'opp_def_qb_cmp', 'jets_qb_cmp', 'opp_def_qb_att', 'jets_qb_att', 'opp_def_qb_pass_yds', 'jets_qb_pass_yds', 'opp_def_qb_pass_td', 'jets_qb_pass_td', 'opp_def_qb_int', 'jets_qb_int', 'opp_def_qb_rating', 'jets_qb_rating', 'opp_def_qb_sacked', 'jets_qb_sacked', 'opp_def_qb_rush_att', 'jets_qb_rush_att', 'opp_def_qb_rush_yds', 'jets_qb_rush_yds', 'opp_def_qb_rush_td', 'jets_qb_rush_td', 'opp_def_qb_comp_percent', 'jets_qb_comp_percent', 'opp_def_qb_yd_att', 'jets_qb_yd_att', 'opp_def_qb_td_percent', 'jets_qb_td_percent', 'opp_def_qb_int_percent', 'jets_qb_int_percent', 'opp_avg_result', 'opp_avg_points_for', 'opp_avg_points_allowed', 'opp_avg_tot_yds', 'opp_avg_pass_yds', 'opp_avg_rush_yds', 'opp_avg_opp_tot_yds', 'opp_avg_opp_pass_yds', 'opp_avg_opp_rush_yds', 'points_for_over_expected', 'points_allowed_over_expected', 'tot_yds_over_expected', 'rush_yds_over_expected', 'pass_yds_over_expected', 'opp_tot_yds_over_expected', 'opp_rush_yds_over_expected', 'opp_pass_yds_over_expected', 'win_percent_over_expected', 'jets_qb_cmp_over_expected', 'jets_qb_cmp_over_expected_percent', 'jets_qb_att_over_expected', 'jets_qb_att_over_expected_percent', 'jets_qb_pass_yds_over_expected', 'jets_qb_pass_yds_over_expected_percent', 'jets_qb_pass_td_over_expected', 'jets_qb_pass_td_over_expected_percent', 'jets_qb_int_over_expected', 'jets_qb_int_over_expected_percent', 'jets_qb_rating_over_expected', 'jets_qb_rating_over_expected_percent', 'jets_qb_sacked_over_expected', 'jets_qb_sacked_over_expected_percent', 'jets_qb_rush_att_over_expected', 'jets_qb_rush_att_over_expected_percent', 'jets_qb_rush_yds_over_expected', 'jets_qb_rush_yds_over_expected_percent', 'jets_qb_rush_td_over_expected', 'jets_qb_rush_td_over_expected_percent', 'jets_qb_comp_percent_over_expected', 'jets_qb_comp_percent_over_expected_percent', 'jets_qb_yd_att_over_expected', 'jets_qb_yd_att_over_expected_percent', 'jets_qb_td_percent_over_expected', 'jets_qb_td_percent_over_expected_percent', 'jets_qb_int_percent_over_expected', 'jets_qb_int_percent_over_expected_percent']
        # print('gamelog_column_list', gamelog_column_list)
        # gamelog_column_list = [x for x in gamelog_column_list if not 'over_expected' in x]
        # gamelog_column_list = ['result', 'points_for', 'tot_yds', 'pass_yds', 'rush_yds', 'opp_def_qb_cmp', 'jets_qb_cmp', 'opp_def_qb_att', 'jets_qb_att', 'opp_def_qb_pass_yds', 'jets_qb_pass_yds', 'opp_def_qb_pass_td', 'jets_qb_pass_td', 'opp_def_qb_int', 'jets_qb_int', 'opp_def_qb_rating', 'jets_qb_rating', 'opp_def_qb_rush_yds', 'jets_qb_rush_yds', 'opp_def_qb_rush_td', 'jets_qb_rush_td', 'opp_def_qb_comp_percent', 'jets_qb_comp_percent', 'opp_def_qb_yd_att', 'jets_qb_yd_att', 'opp_avg_result', 'opp_avg_points_for', 'opp_avg_points_allowed', 'opp_avg_opp_tot_yds', 'opp_avg_opp_pass_yds', 'opp_avg_opp_rush_yds', 'points_for_over_expected', 'tot_yds_over_expected', 'rush_yds_over_expected', 'pass_yds_over_expected', 'win_percent_over_expected', 'jets_qb_cmp_over_expected', 'jets_qb_pass_yds_over_expected', 'jets_qb_rating_over_expected', 'jets_qb_rush_yds_over_expected', 'jets_qb_rush_td_over_expected', 'jets_qb_comp_percent_over_expected', 'jets_qb_yd_att_over_expected']
        # gamelog_column_list = ['week', 'opp', 'result', 'opp_avg_result', 'win_percent_over_expected', 'points_for', 'opp_avg_points_allowed', 'points_for_over_expected','tot_yds', 'opp_avg_opp_tot_yds', 'tot_yds_over_expected','jets_qb_pass_yds', 'opp_def_qb_pass_yds', 'pass_yds', 'opp_avg_opp_pass_yds',  'pass_yds_over_expected', 'jets_qb_pass_yds_over_expected', 'rush_yds', 'opp_avg_opp_rush_yds', 'rush_yds_over_expected', 'jets_qb_rating', 'opp_def_qb_rating', 'jets_qb_rating_over_expected','jets_qb_yd_att', 'opp_def_qb_yd_att','jets_qb_yd_att_over_expected']
        gamelog_column_list = ['week', 'opp', 'result', 'opp_avg_result', 'win_percent_over_expected', 'points_for', 'opp_avg_points_allowed', 'points_for_over_expected','tot_yds', 'opp_avg_opp_tot_yds', 'tot_yds_over_expected', 'pass_yds', 'opp_avg_opp_pass_yds',  'pass_yds_over_expected', 'rush_yds', 'opp_avg_opp_rush_yds', 'rush_yds_over_expected', 'jets_qb_rating', 'opp_def_qb_rating', 'jets_qb_rating_over_expected','jets_qb_yd_att', 'opp_def_qb_yd_att','jets_qb_yd_att_over_expected']
        with_zach_since_2022 = with_zach_since_2022[gamelog_column_list]
        without_zach_since_2022 = without_zach_since_2022[gamelog_column_list]
        with_zach_since_2022 = with_zach_since_2022.rename(columns={'result':'W%', 'opp_avg_result':'exp_W%', 'win_percent_over_expected':'W% +/- exp', 'points_for':'pts', 'opp_avg_points_allowed':'exp_pts', 'points_for_over_expected': 'pts +/- exp','tot_yds':'tot_yds', 'opp_avg_opp_tot_yds':'exp_tot_yds', 'tot_yds_over_expected': 'tot_yds +/- exp', 'pass_yds':'pass_yds', 'opp_avg_opp_pass_yds':'exp_pass_yds',  'pass_yds_over_expected': 'pass_yds +/- exp', 'rush_yds':'rush_yds', 'opp_avg_opp_rush_yds':'exp_rush_yds', 'rush_yds_over_expected':'rush_yds +/- exp', 'jets_qb_rating':'pass_rtg', 'opp_def_qb_rating':'exp_pass_rtg', 'jets_qb_rating_over_expected':'pass_rtg +/- exp', 'jets_qb_yd_att':'yd_att', 'opp_def_qb_yd_att':'exp_yd_att', 'jets_qb_yd_att_over_expected':'yd_att +/- exp'})
        without_zach_since_2022 = without_zach_since_2022.rename(columns={'result':'W%', 'opp_avg_result':'exp_W%', 'win_percent_over_expected':'W% +/- exp', 'points_for':'pts', 'opp_avg_points_allowed':'exp_pts', 'points_for_over_expected': 'pts +/- exp','tot_yds':'tot_yds', 'opp_avg_opp_tot_yds':'exp_tot_yds', 'tot_yds_over_expected': 'tot_yds +/- exp', 'pass_yds':'pass_yds', 'opp_avg_opp_pass_yds':'exp_pass_yds',  'pass_yds_over_expected': 'pass_yds +/- exp', 'rush_yds':'rush_yds', 'opp_avg_opp_rush_yds':'exp_rush_yds', 'rush_yds_over_expected':'rush_yds +/- exp', 'jets_qb_rating':'pass_rtg', 'opp_def_qb_rating':'exp_pass_rtg', 'jets_qb_rating_over_expected':'pass_rtg +/- exp', 'jets_qb_yd_att':'yd_att', 'opp_def_qb_yd_att':'exp_yd_att', 'jets_qb_yd_att_over_expected':'yd_att +/- exp'})
        with_zach_since_2022['exp_W%'] = 1 - with_zach_since_2022['exp_W%']
        without_zach_since_2022['exp_W%'] = 1 - without_zach_since_2022['exp_W%']


        # mean_column_list = with_zach_means_since_2022.columns.tolist()
        mean_column_list = ['yr', 'wk', 'opp', 'result', 'points_for', 'points_for_over_expected', 'points_allowed', 'tot_yds', 'pass_yds', 'rush_yds', 'opp_tot_yds', 'opp_pass_yds', 'opp_rush_yds', 'opp_def_qb_cmp', 'jets_qb_cmp', 'opp_def_qb_att', 'jets_qb_att', 'opp_def_qb_pass_yds', 'jets_qb_pass_yds', 'opp_def_qb_pass_td', 'jets_qb_pass_td', 'opp_def_qb_int', 'jets_qb_int', 'opp_def_qb_rating', 'jets_qb_rating', 'opp_def_qb_sacked', 'jets_qb_sacked', 'opp_def_qb_rush_att', 'jets_qb_rush_att', 'opp_def_qb_rush_yds', 'jets_qb_rush_yds', 'opp_def_qb_rush_td', 'jets_qb_rush_td', 'opp_def_qb_comp_percent', 'jets_qb_comp_percent', 'opp_def_qb_yd_att', 'jets_qb_yd_att', 'opp_def_qb_td_percent', 'jets_qb_td_percent', 'opp_def_qb_int_percent', 'jets_qb_int_percent', 'opp_avg_result', 'opp_avg_points_for', 'opp_avg_points_allowed', 'opp_avg_tot_yds', 'opp_avg_pass_yds', 'opp_avg_rush_yds', 'opp_avg_opp_tot_yds', 'opp_avg_opp_pass_yds', 'opp_avg_opp_rush_yds', 'points_for_over_expected', 'points_allowed_over_expected', 'tot_yds_over_expected', 'rush_yds_over_expected', 'pass_yds_over_expected', 'opp_tot_yds_over_expected', 'opp_rush_yds_over_expected', 'opp_pass_yds_over_expected', 'win_percent_over_expected', 'jets_qb_cmp_over_expected', 'jets_qb_cmp_over_expected_percent', 'jets_qb_att_over_expected', 'jets_qb_att_over_expected_percent', 'jets_qb_pass_yds_over_expected', 'jets_qb_pass_yds_over_expected_percent', 'jets_qb_pass_td_over_expected', 'jets_qb_pass_td_over_expected_percent', 'jets_qb_int_over_expected', 'jets_qb_int_over_expected_percent', 'jets_qb_rating_over_expected', 'jets_qb_rating_over_expected_percent', 'jets_qb_sacked_over_expected', 'jets_qb_sacked_over_expected_percent', 'jets_qb_rush_att_over_expected', 'jets_qb_rush_att_over_expected_percent', 'jets_qb_rush_yds_over_expected', 'jets_qb_rush_yds_over_expected_percent', 'jets_qb_rush_td_over_expected', 'jets_qb_rush_td_over_expected_percent', 'jets_qb_comp_percent_over_expected', 'jets_qb_comp_percent_over_expected_percent', 'jets_qb_yd_att_over_expected', 'jets_qb_yd_att_over_expected_percent', 'jets_qb_td_percent_over_expected', 'jets_qb_td_percent_over_expected_percent', 'jets_qb_int_percent_over_expected', 'jets_qb_int_percent_over_expected_percent']
        # print('mean_column_list', mean_column_list)
        # mean_column_list = ['jets_qb_cmp','jets_qb_att','jets_qb_pass_yds','jets_qb_pass_td','jets_qb_int','jets_qb_rating','jets_qb_sacked','jets_qb_rush_att','jets_qb_rush_yds','jets_qb_rush_td','jets_qb_comp_percent','jets_qb_yd_att','jets_qb_td_percent','jets_qb_int_percent']
        # mean_column_list = [x for x in mean_column_list if not 'over_expected' in x]
        # mean_column_list = ['result', 'points_for', 'points_allowed', 'tot_yds', 'pass_yds', 'rush_yds', 'opp_def_qb_cmp', 'jets_qb_cmp', 'opp_def_qb_att', 'jets_qb_att', 'opp_def_qb_pass_yds', 'jets_qb_pass_yds', 'opp_def_qb_pass_td', 'jets_qb_pass_td', 'opp_def_qb_int', 'jets_qb_int', 'opp_def_qb_rating', 'jets_qb_rating', 'opp_def_qb_rush_yds', 'jets_qb_rush_yds', 'opp_def_qb_rush_td', 'jets_qb_rush_td', 'opp_def_qb_comp_percent', 'jets_qb_comp_percent', 'opp_def_qb_yd_att', 'jets_qb_yd_att', 'opp_def_qb_td_percent', 'jets_qb_td_percent', 'opp_def_qb_int_percent', 'jets_qb_int_percent', 'opp_avg_result','opp_avg_points_allowed', 'opp_avg_opp_tot_yds', 'opp_avg_opp_pass_yds', 'opp_avg_opp_rush_yds', 'points_for_over_expected', 'tot_yds_over_expected', 'rush_yds_over_expected', 'pass_yds_over_expected', 'win_percent_over_expected', 'jets_qb_cmp_over_expected', 'jets_qb_pass_yds_over_expected', 'jets_qb_pass_td_over_expected', 'jets_qb_int_over_expected', 'jets_qb_rating_over_expected', 'jets_qb_rush_yds_over_expected', 'jets_qb_rush_td_over_expected', 'jets_qb_comp_percent_over_expected', 'jets_qb_yd_att_over_expected', 'jets_qb_td_percent_over_expected', 'jets_qb_int_percent_over_expected']
        mean_column_list = ['result', 'opp_avg_result', 'win_percent_over_expected', 'points_for', 'opp_avg_points_allowed', 'points_for_over_expected','tot_yds', 'opp_avg_opp_tot_yds', 'tot_yds_over_expected', 'pass_yds', 'opp_avg_opp_pass_yds',  'pass_yds_over_expected', 'rush_yds', 'opp_avg_opp_rush_yds', 'rush_yds_over_expected', 'jets_qb_rating', 'opp_def_qb_rating', 'jets_qb_rating_over_expected', 'jets_qb_yd_att', 'opp_def_qb_yd_att', 'jets_qb_yd_att_over_expected']
        with_zach_means_since_2022 = with_zach_means_since_2022[mean_column_list]
        without_zach_means_since_2022 = without_zach_means_since_2022[mean_column_list]
        with_zach_means_since_2022 = with_zach_means_since_2022.rename(columns={'result':'W%', 'opp_avg_result':'exp_W%', 'win_percent_over_expected':'W% +/- exp', 'points_for':'pts', 'opp_avg_points_allowed':'exp_pts', 'points_for_over_expected': 'pts +/- exp','tot_yds':'tot_yds', 'opp_avg_opp_tot_yds':'exp_tot_yds', 'tot_yds_over_expected': 'tot_yds +/- exp', 'pass_yds':'pass_yds', 'opp_avg_opp_pass_yds':'exp_pass_yds',  'pass_yds_over_expected': 'pass_yds +/- exp', 'rush_yds':'rush_yds', 'opp_avg_opp_rush_yds':'exp_rush_yds', 'rush_yds_over_expected':'rush_yds +/- exp', 'jets_qb_rating':'pass_rtg', 'opp_def_qb_rating':'exp_pass_rtg', 'jets_qb_rating_over_expected':'pass_rtg +/- exp', 'jets_qb_yd_att':'yd_att', 'opp_def_qb_yd_att':'exp_yd_att', 'jets_qb_yd_att_over_expected':'yd_att +/- exp'})
        without_zach_means_since_2022 = without_zach_means_since_2022.rename(columns={'result':'W%', 'opp_avg_result':'exp_W%', 'win_percent_over_expected':'W% +/- exp', 'points_for':'pts', 'opp_avg_points_allowed':'exp_pts', 'points_for_over_expected': 'pts +/- exp','tot_yds':'tot_yds', 'opp_avg_opp_tot_yds':'exp_tot_yds', 'tot_yds_over_expected': 'tot_yds +/- exp', 'pass_yds':'pass_yds', 'opp_avg_opp_pass_yds':'exp_pass_yds',  'pass_yds_over_expected': 'pass_yds +/- exp', 'rush_yds':'rush_yds', 'opp_avg_opp_rush_yds':'exp_rush_yds', 'rush_yds_over_expected':'rush_yds +/- exp', 'jets_qb_rating':'pass_rtg', 'opp_def_qb_rating':'exp_pass_rtg', 'jets_qb_rating_over_expected':'pass_rtg +/- exp', 'jets_qb_yd_att':'yd_att', 'opp_def_qb_yd_att':'exp_yd_att', 'jets_qb_yd_att_over_expected':'yd_att +/- exp'})
        with_zach_means_since_2022['exp_W%'] = 1 - with_zach_means_since_2022['exp_W%']
        without_zach_means_since_2022['exp_W%'] = 1 - without_zach_means_since_2022['exp_W%']





        # print('JETS WITH ZACH WILSON GAMELOGS 2022')
        # # print(with_zach_since_2022.to_string(index=False, justify='left'))
        # table = tabulate(with_zach_since_2022, headers='keys', tablefmt='pretty')
        # print(table)
        # print('JETS WITHOUT ZACH WILSON GAMELOGS 2022')
        # # print(without_zach_since_2022.to_string(index=False, justify='left'))
        # table = tabulate(without_zach_since_2022, headers='keys', tablefmt='pretty')
        # print(table)

        pretty_table(with_zach_since_2022, title='JETS WITH ZACH WILSON GAMELOGS 2022')
        pretty_table(without_zach_since_2022, title='JETS WITHOUT ZACH WILSON GAMELOGS 2022')

        # print('JETS WITH ZACH WILSON RATE STATISTICS 2022')
        # # print(with_zach_means_since_2022.to_string(index=False, justify='left'))
        # table = tabulate(with_zach_means_since_2022, headers='keys', tablefmt='pretty')
        # print(table)
        # print('JETS WITHOUT ZACH WILSON RATE STATISTICS 2022')
        # table = tabulate(without_zach_means_since_2022, headers='keys', tablefmt='pretty')
        # print(table)
        # print(without_zach_means_since_2022.to_string(index=False, justify='left'))

        pretty_table(with_zach_means_since_2022, title='JETS WITH ZACH WILSON RATE STATISTICS 2022')
        pretty_table(without_zach_means_since_2022, title='JETS WITHOUT ZACH WILSON RATE STATISTICS 2022')


        with_zach_since_2022.to_csv('with_zach_since_2022.csv', index=False)
        without_zach_since_2022.to_csv('without_zach_since_2022.csv', index=False)
        with_zach_means_since_2022.to_csv('with_zach_means_since_2022.csv', index=False)
        without_zach_means_since_2022.to_csv('without_zach_means_since_2022.csv', index=False)


    # if 1:
        # Load the two files
        with_zach = pd.read_csv('with_zach_means_since_2022.csv')
        without_zach = pd.read_csv('without_zach_means_since_2022.csv')

        # # Print the head of the dataframes
        # print(with_zach.head())
        # print(without_zach.head())

        # Transpose the dataframes to switch rows and columns
        with_zach_t = with_zach.transpose()
        without_zach_t = without_zach.transpose()

        # Rename the columns
        with_zach_t.columns = ['With Zach']
        without_zach_t.columns = ['Without Zach']

        # Join the two dataframes
        comparison_df = with_zach_t.join(without_zach_t)
        comparison_df['Difference'] = comparison_df['Without Zach'] - comparison_df['With Zach']

        # numeric_cols = comparison_df.select_dtypes(include='number')
        # comparison_df[numeric_cols.columns] = numeric_cols.round(2)

        # # # Print the head of the comparison dataframe
        # # print(comparison_df.head())

        # table = tabulate(comparison_df, headers='keys', tablefmt='pretty')

        # # print(comparison_df)
        # print(table)

        pretty_table(comparison_df, 'COMPARISON TABLE')
        comparison_df.to_csv('comparison_table.csv', index=True)





if __name__ == "__main__":
    main()



