import requests
import pandas as pd
import time
from bs4 import BeautifulSoup


# Starting URL for QB stats
start_url = "https://www.fantasypros.com/nfl/stats/qb.php?scoring=PPR"

# Function to get all position links from the navbar
def get_position_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'lxml')
    navbar = soup.find('ul', class_='pills pills--horizontal desktop-pills')
    position_links = {a.text.strip(): a.get("href") for a in navbar.find_all('a') if a.get("href") and a.text.strip() in ['QB', 'RB', 'WR', 'TE', 'K', 'DST']}
    return position_links

# Get position links from the start URL
position_links = get_position_links(start_url)

# Define the positions of interest ie: the positions relevant in fantasy football leagues
positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DST']

# Create a dictionary to hold stats for each position
stats_dict = {
    'QB': [],
    'RB': [],
    'WR': [],
    'TE': [],
    'K': [],
    'DST': []
}

# Function to clean the DataFrame
def clean_df(df):
    # Flatten the MultiIndex columns
    df.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df.columns]
    
    # Drop the unnecessary columns
    df = df.drop(columns=['Unnamed: 0_level_0_Rank', 'Position', 'Rank', 'Position_'], errors='ignore')
    
    # Rename columns
    df.rename(columns={'Unnamed: 1_level_0_Player': 'Player'}, inplace=True)
    
    return df

# Function to rename specific columns
def rename_cols(df):
    
    rename_dict = {
        'misc_fl': 'fumbles_lost',
        'misc_g': 'games_played',
        'misc_fpts': 'fantasy_points',
        'misc_fpts/g': 'fantasy_points_per_game',
        'misc_rost': 'percent_rostered',
        'g': 'games_played',
        'fpts': 'fantasy_points',
        'fpts/g': 'fantasy_points_per_game',
        'rost': 'percent_rostered'
    }
    df.rename(columns=rename_dict, inplace=True)
    # Make sure all columns that can be compared are numeric and remove the percentage sign
    df['percent_rostered'] = df['percent_rostered'].str.rstrip('%').astype('float')

# Loop through each position link and fetch the table data
for position in positions:
    link = f"https://www.fantasypros.com/nfl/stats/{position.lower()}.php"
    tables = pd.read_html(link)
    # Get the first table in the list
    position_df = tables[0]
    position_df['Position'] = position
    
    # Clean the DataFrame
    position_df = clean_df(position_df)
    
    # Append the cleaned DataFrame to the appropriate list in the dictionary
    stats_dict[position].append(position_df)
    
    #Try to avoid getting blocked
    time.sleep(5)


# Concatenate all DataFrames within each position's list if needed
for position in positions:
    stats_dict[position] = pd.concat(stats_dict[position], ignore_index=True) if stats_dict[position] else pd.DataFrame()
    stats_dict[position].columns = stats_dict[position].columns.str.lower()

# Rename columns for all DataFrames in the dictionary
for position in positions:
    rename_cols(stats_dict[position])

# Rename the 'player' column to 'team' in the DST_stats_df
# Do this separately since DST is the only one that is a team stat 
stats_dict['DST'].rename(columns={'player': 'team'}, inplace=True)


# Extract DataFrames for each position
QB_stats_df = stats_dict['QB']
RB_stats_df = stats_dict['RB']
WR_stats_df = stats_dict['WR']
TE_stats_df = stats_dict['TE']
K_stats_df = stats_dict['K']
DST_stats_df = stats_dict['DST']

# Save each DataFrame to a CSV file
QB_stats_df.to_csv('data/QB_stats.csv', index=False)
RB_stats_df.to_csv('data/RB_stats.csv', index=False)
WR_stats_df.to_csv('data/WR_stats.csv', index=False)
TE_stats_df.to_csv('data/TE_stats.csv', index=False)
K_stats_df.to_csv('data/K_stats.csv', index=False)
DST_stats_df.to_csv('data/DST_stats.csv', index=False)