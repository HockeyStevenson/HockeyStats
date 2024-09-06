import numpy as np
import os, sys
from numpy import array
import altair as alt
import plotly.express as px


sys.path.insert(1, './shared')

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objs as go
import base64
import boto3
from io import BytesIO
from openpyxl import load_workbook


#st.set_option('deprecation.showPyplotGlobalUse', False)
# Use the Access Key and Secret Key you just created

AWS_ACCESS_KEY = st.secrets["aws"]["AWS_ACCESS_KEY"]
AWS_SECRET_KEY = st.secrets["aws"]["AWS_SECRET_KEY"]

S3_BUCKET = 'stevensonhockeydata'
EXCEL_FILE_KEY = 'Stevenson_Hockey.xlsx' 

# Create an S3 client
s3 = boto3.client('s3', aws_access_key_id=AWS_ACCESS_KEY, aws_secret_access_key=AWS_SECRET_KEY)



# Function to load an image and convert it to base64
def get_image_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode()

# Image URL
logo_url = "./stevenson_logo.png"

# Get the base64 string of the image
logo_base64 = get_image_base64(logo_url)



# Page configuration
st.set_page_config(
    page_title="Stevenson Hockey Dashboard",
    page_icon=f"data:image/png;base64,{logo_base64}",
    layout="wide",
    initial_sidebar_state="expanded")



# HTML and CSS for centering the image
st.sidebar.markdown(
    f"""
    <div style="display: flex; justify-content: center;">
        <img src="data:image/png;base64,{logo_base64}" width="100">
    </div>
    """,
    unsafe_allow_html=True
)


###############################################################

# Load data
#data = pd.ExcelFile('Stevenson_Hockey.xlsx')


# Load the sheets into separate DataFrames
#roster_df = pd.read_excel(data, sheet_name='Roster')
#scoring_df = pd.read_excel(data, sheet_name='Scoring')
#penalties_df = pd.read_excel(data, sheet_name='Penalties')
#shots_df = pd.read_excel(data, sheet_name='Shots')
#faceoff_df = pd.read_excel(data, sheet_name='Faceoff')


###############################################################


def read_excel_from_s3(bucket, file_key, sheet_name):
    # Get the object from S3
    obj = s3.get_object(Bucket=bucket, Key=file_key)
    
    # Read the content of the file into a Pandas DataFrame
    excel_data = obj['Body'].read()
    df = pd.read_excel(BytesIO(excel_data), sheet_name=sheet_name)
    
    return df

# Read the "roster" worksheet from the Excel file
roster_df = read_excel_from_s3(S3_BUCKET, EXCEL_FILE_KEY, sheet_name="Roster")
scoring_df = read_excel_from_s3(S3_BUCKET, EXCEL_FILE_KEY, sheet_name="Scoring")
penalties_df = read_excel_from_s3(S3_BUCKET, EXCEL_FILE_KEY, sheet_name="Penalties")
shots_df = read_excel_from_s3(S3_BUCKET, EXCEL_FILE_KEY, sheet_name="Shots")
faceoff_df = read_excel_from_s3(S3_BUCKET, EXCEL_FILE_KEY, sheet_name="Faceoff")



# Sidebar
with st.sidebar:
    st.subheader('Stevenson Hockey Dashboard')
    
    team_list = list(roster_df.Team.unique())[::-1]
    
    selected_team = st.selectbox('Select a team', team_list)
    df_selected_team = roster_df[roster_df.Team == selected_team]
    df_selected_team_sorted = df_selected_team.sort_values(by="JerseyNumber", ascending=False)


    # Sidebar options
    st.sidebar.title("Select Options")
    #view_by = st.sidebar.radio("View By", ["Team", "Player", "Game"])
    view_by = st.sidebar.radio("View By", ["Team", "Player"])
    

#######################




# final_scoring_df, final_penalties_df, final_shooting_df

scoring_stevenson = scoring_df[scoring_df['ScoringTeam'] == 'Stevenson']

# Perform the merge for 'Stevenson' team
scoring_merged_stevenson = pd.merge(
    scoring_stevenson,
    roster_df[['Team', 'JerseyNumber', 'FirstName', 'LastName', 'Position']],
    how='left',
    left_on=['Team', 'Goal'],
    right_on=['Team', 'JerseyNumber']
)

# Filter out non-Stevenson scoring records and concatenate them back with the merged Stevenson data
scoring_non_stevenson = scoring_df[scoring_df['ScoringTeam'] != 'Stevenson']

# Combine the Stevenson merged scoring data with non-Stevenson scoring data
final_scoring_df = pd.concat([scoring_merged_stevenson, scoring_non_stevenson], ignore_index=True)


# Convert the 'GameDate' to a string format (YYYY-MM-DD)
final_scoring_df['FormattedDate'] = pd.to_datetime(final_scoring_df['GameDate']).dt.strftime('%Y-%m-%d')

# Optionally, if you want to replace the original 'GameDate' column:
final_scoring_df['GameDate'] = final_scoring_df['FormattedDate']
final_scoring_df.drop(columns=['FormattedDate'], inplace=True)







penalties_stevenson = penalties_df[penalties_df['PenaltyTeam'] == 'Stevenson']

# Perform the merge for 'Stevenson' team
penalties_merged_stevenson = pd.merge(
    penalties_stevenson,
    roster_df[['Team', 'JerseyNumber', 'FirstName', 'LastName', 'Position']],
    how='left',
    left_on=['Team', 'JerseyNumber'],
    right_on=['Team', 'JerseyNumber']
)

# Filter out non-Stevenson penalties and concatenate them back with the merged Stevenson data
penalties_non_stevenson = penalties_df[penalties_df['PenaltyTeam'] != 'Stevenson']

# Combine the Stevenson merged penalties with non-Stevenson penalties
final_penalties_df = pd.concat([penalties_merged_stevenson, penalties_non_stevenson], ignore_index=True)

# Convert the 'GameDate' to a string format (YYYY-MM-DD)
final_penalties_df['FormattedDate'] = pd.to_datetime(final_penalties_df['GameDate']).dt.strftime('%Y-%m-%d')

# Optionally, if you want to replace the original 'GameDate' column:
final_penalties_df['GameDate'] = final_penalties_df['FormattedDate']
final_penalties_df.drop(columns=['FormattedDate'], inplace=True)









shots_stevenson = shots_df[shots_df['ShootingTeam'] == 'Stevenson']

# Perform the merge for 'Stevenson' team
shots_merged_stevenson = pd.merge(
    shots_stevenson,
    roster_df[['Team', 'JerseyNumber', 'FirstName', 'LastName', 'Position']],
    how='left',
    left_on=['Team', 'JerseyNumber'],
    right_on=['Team', 'JerseyNumber']
)

# Filter out non-Stevenson shooting records and concatenate them back with the merged Stevenson data
shots_non_stevenson = shots_df[shots_df['ShootingTeam'] != 'Stevenson']

# Combine the Stevenson merged shooting data with non-Stevenson shooting data
final_shots_df = pd.concat([shots_merged_stevenson, shots_non_stevenson], ignore_index=True)


# Convert the 'GameDate' to a string format (YYYY-MM-DD)
final_shots_df['FormattedDate'] = pd.to_datetime(final_shots_df['GameDate']).dt.strftime('%Y-%m-%d')

# Optionally, if you want to replace the original 'GameDate' column:
final_shots_df['GameDate'] = final_shots_df['FormattedDate']
final_shots_df.drop(columns=['FormattedDate'], inplace=True)



# Add a horizontal line
st.markdown("<hr>", unsafe_allow_html=True)
#metric = st.radio("Metric", ["Shooting", "Penalties", "Game Outcomes"])



if view_by == "Team":
    
    #st.subheader("Hockey Data Analysis")
    
    team_outcomes = final_scoring_df[final_scoring_df['Team'] == selected_team]
    
    # Add "All" as an option in the dropdown
    opponent_options = ["All"] + list(team_outcomes['Opponent'].unique())

    # Create the selectbox with "All" as the default value
    selected_opponent = st.sidebar.selectbox("Select Opponent", opponent_options, index=0)
    
    
    if selected_opponent != "All":
        st.subheader(f"Hockey Data Analysis: Stevenson vs. {selected_opponent}") 
    else:
        st.subheader("Hockey Data Analysis: Stevenson")
    
    

    # Filter the data if a specific opponent is selected (i.e., not "All")
    #if selected_opponent != "All":
        #filtered_data = team_outcomes[team_outcomes['Opponent'] == selected_opponent]
    #else:
        #filtered_data = team_outcomes
    
    #st.write(selected_opponent)
    
    
    metric = st.radio("Metric", ["Game Outcomes", "Shots", "Penalties", "Faceoff"])
    
    # Add a horizontal line
    st.markdown("<hr>", unsafe_allow_html=True)
    
    if metric == "Game Outcomes":
 
        temp_team_outcomes = final_scoring_df[final_scoring_df['Team'] == selected_team]

        if selected_opponent != "All":
                team_outcomes = temp_team_outcomes[temp_team_outcomes['Opponent'] == selected_opponent]
        else:
                team_outcomes = temp_team_outcomes   
    
    
    
    
        if team_outcomes.empty:
                st.subheader(f"No Game Data for {selected_team} against {selected_opponent}")
        else:    
                # Calculate total unique games played
                total_games = team_outcomes[['GameDate', 'Team', 'Opponent']].drop_duplicates().shape[0]
                


                
                #st.dataframe(team_outcomes)
             

                # Calculate total unique wins
                total_wins = team_outcomes[team_outcomes['Win'].str.lower() == 'yes'][['GameDate', 'Team', 'Opponent', 'Win']].drop_duplicates().shape[0]

                # Calculate winning rate
                win_rate = (total_wins / total_games) * 100 if total_games > 0 else 0

                # Calculate home and away games
                home_games = team_outcomes[team_outcomes['Home'].str.lower() == 'yes']
                away_games = team_outcomes[team_outcomes['Home'].str.lower() != 'yes']

                total_home_games = home_games[['GameDate', 'Team', 'Opponent']].drop_duplicates().shape[0]
                total_away_games = away_games[['GameDate', 'Team', 'Opponent']].drop_duplicates().shape[0]

                # Calculate home and away wins
                home_wins = home_games[home_games['Win'].str.lower() == 'yes'][['GameDate', 'Team', 'Opponent', 'Win']].drop_duplicates().shape[0]
                away_wins = away_games[away_games['Win'].str.lower() == 'yes'][['GameDate', 'Team', 'Opponent', 'Win']].drop_duplicates().shape[0]

                # Calculate winning rates
                home_win_rate = (home_wins / total_home_games) * 100 if total_home_games > 0 else 0
                away_win_rate = (away_wins / total_away_games) * 100 if total_away_games > 0 else 0

                # Create columns for the summary stats
                col1, col2, col3 = st.columns(3)
                col1.metric("Total Games Played", total_games)
                col2.metric("Total Games Won", total_wins)
                col3.metric("Winning Rate", f"{win_rate:.1f}%")


                col4, col5, col6 = st.columns(3)
                col4.metric("Home Games", total_home_games)
                col5.metric("Home Games Won", home_wins)
                col6.metric("Home Win Rate", f"{home_win_rate:.1f}%")


                col7, col8, col9 = st.columns(3)
                col7.metric("Away Games", total_away_games)
                col8.metric("Away Games Won", away_wins)
                col9.metric("Away Win Rate", f"{away_win_rate:.1f}%")           


                
                
                # Add a horizontal line
                st.markdown("<hr>", unsafe_allow_html=True)

                
                # Function to create a gauge chart
                def create_gauge(title, value):
                    fig = go.Figure(go.Indicator(
                        mode="gauge+number",
                        value=value,
                        title={'text': title},
                        gauge={'axis': {'range': [0, 100]},
                               'bar': {'color': 'rgb(41,77,46)'},
                               'steps': [
                                   {'range': [0, 50], 'color': "lightgray"},
                                   {'range': [50, 75], 'color': "gray"},
                                   {'range': [75, 100], 'color': "lightblue"}]
                              }))
                    return fig

                # Create columns for the gauges
                col1, col2, col3 = st.columns(3)

                col1.plotly_chart(create_gauge("Total Win Rate", win_rate), use_container_width=True)
                col2.plotly_chart(create_gauge("Home Win Rate", home_win_rate), use_container_width=True)
                col3.plotly_chart(create_gauge("Away Win Rate", away_win_rate), use_container_width=True)


                # Add a horizontal line
                st.markdown("<hr>", unsafe_allow_html=True)

                
                
                
                # Prepare data for the scores bar chart
                scores_data = team_outcomes[['GameDate', 'Opponent', 'ScoreStevenson', 'ScoreOpponent']].drop_duplicates()
                scores_data = scores_data.sort_values(by='GameDate')  # Sort by game date for better visual order
                
                #st.dataframe(scores_data)
                
                # Create hovertext
                stevenson_hovertext = ['Stevenson' for _ in range(len(scores_data))]
                opponent_hovertext = scores_data['Opponent']

                # Create the bar chart
                fig = go.Figure(data=[
                    go.Bar(
                        name='Stevenson',
                        x=scores_data['GameDate'],
                        y=scores_data['ScoreStevenson'],
                        marker_color='rgb(41,77,46)',
                        hovertext=stevenson_hovertext,
                        hoverinfo='text+y'
                    ),
                    go.Bar(
                        name='Opponent',
                        x=scores_data['GameDate'],
                        y=scores_data['ScoreOpponent'],
                        hovertext=opponent_hovertext,
                        hoverinfo='text+y'
                    )
                ])

                # Update layout and set x-axis to categorical to show only the dates in your DataFrame
                fig.update_layout(
                    barmode='group',
                    title="Scores by Stevenson and Opponent by Game",
                    xaxis_title="Game Date",
                    yaxis_title="Scores",
                    xaxis={'type': 'category'}  # Setting the x-axis type to category
                )

                # Display the bar chart in Streamlit
                st.plotly_chart(fig, use_container_width=True)                
                
                # Add a horizontal line
                st.markdown("<hr>", unsafe_allow_html=True)
          
                #st.dataframe(team_outcomes)
                #st.write(selected_team)
                
                stevenson_scores = team_outcomes[(team_outcomes['ScoringTeam'] == 'Stevenson') & (team_outcomes['Team'] == selected_team)]

                
                #st.dataframe(stevenson_scores)
                
                # Group by jersey number and name, then count scores
                score_counts = stevenson_scores.groupby(['JerseyNumber', 'Team','FirstName','LastName','Position']).size().reset_index(name='TotalScores')
                
                # Merging player counts with roster to include player names
                #scored_players = pd.merge(score_counts, roster_df, on='JerseyNumber', how='left')
                

                # Sort the scores in descending order
                sorted_scores = score_counts.sort_values(by='TotalScores', ascending=False)
                

                st.subheader("Sorted Scores by Player for Stevenson")
                st.dataframe(sorted_scores.set_index('JerseyNumber'), width=650)

                
                # Add a horizontal line
                st.markdown("<hr>", unsafe_allow_html=True)
                
                #st.dataframe(team_outcomes)

                
                # Selecting the required columns and filtering by 'ScoringTeam'
                assistants_player1 = team_outcomes[team_outcomes['ScoringTeam'] == 'Stevenson'][['GameDate', 'Team', 'Opponent', 'Assistant_1']]

                # Renaming 'Assistant_1' to 'JerseyNumber'
                assistants_player1 = assistants_player1.rename(columns={'Assistant_1': 'JerseyNumber'})
                
                # Selecting the required columns and filtering by 'ScoringTeam'
                assistants_player2 = team_outcomes[team_outcomes['ScoringTeam'] == 'Stevenson'][['GameDate', 'Team', 'Opponent', 'Assistant_2']]

                # Renaming 'Assistant_1' to 'JerseyNumber'
                assistants_player2 = assistants_player2.rename(columns={'Assistant_2': 'JerseyNumber'})                
                
                #assistants_player = team_outcomes[team_outcomes['ShootingTeam'] == 'Stevenson'].groupby(['GameDate', 'Team', 'Opponent',]).size().reset_index(name='TotalStevensonShots')
      
                assistants_player = pd.concat([assistants_player1, assistants_player2], axis=0)

                # Reset the index after concatenation, if needed
                assistants_player = assistants_player.reset_index(drop=True)
                assistants_player = assistants_player.dropna(subset=['JerseyNumber'])
                
                
                # Counting the number of records for each JerseyNumber
                player_counts = assistants_player.groupby('JerseyNumber').size().reset_index(name='TotalAssistants')

                #player_counts = assistants_player.groupby(['JerseyNumber', 'Team','FirstName','LastName','Position']).size().reset_index(name='TotalAssistants')
                

                # Sorting by RecordCount in descending order
                player_counts = player_counts.sort_values(by='TotalAssistants', ascending=False)
                
                
                # Merging player counts with roster to include player names
                ranked_players = pd.merge(player_counts, roster_df, on='JerseyNumber', how='left')

                

                st.subheader("Sorted Assistants by Player for Stevenson")
                #st.dataframe(assistants_player.set_index('JerseyNumber'))
                #st.dataframe(player_counts.set_index('JerseyNumber'))
                ranked_players = ranked_players[['JerseyNumber', 'Team', 'FirstName', 'LastName', 'Position', 'TotalAssistants']]
                st.dataframe(ranked_players.set_index('JerseyNumber'), width=650)


            
            
            
    
    if metric == "Shots":   
        temp_team_shooting = final_shots_df[final_shots_df['Team'] == selected_team]


        if selected_opponent != "All":
                team_outcomes = temp_team_shooting[temp_team_shooting['Opponent'] == selected_opponent]
                team_scoring = final_shots_df[(final_shots_df['Team'] == selected_team) & (final_shots_df['Opponent'] == selected_opponent)]
                team_shooting = final_shots_df[(final_shots_df['Team'] == selected_team) & (final_shots_df['Opponent'] == selected_opponent)]

                
        else:
                team_outcomes = temp_team_shooting   
                team_scoring = final_scoring_df[final_scoring_df['Team'] == selected_team]
                team_shooting = final_shots_df[final_shots_df['Team'] == selected_team]            
        
        
        
        if team_shooting.empty:
                st.subheader(f"No Shooting Data for {selected_team}")
        else:


                # Filter the data for the selected team
                #team_scoring = final_scoring_df[final_scoring_df['Team'] == selected_team]
                #team_shooting = final_shots_df[final_shots_df['Team'] == selected_team]
                
                #st.dataframe(team_shooting)
                
                 # Aggregate shooting data by game for Stevenson
                shooting_summary_team = team_shooting[team_shooting['ShootingTeam'] == 'Stevenson'].groupby(['GameDate', 'Team', 'Opponent']).size().reset_index(name='TotalStevensonShots')

                # Aggregate shooting data by game for Opponents
                # Assuming 'final_shots_df' should be 'team_shooting', as 'final_shots_df' is not previously defined
                shooting_summary_opponent = team_shooting[team_shooting['ShootingTeam'] != 'Stevenson'].groupby(['GameDate', 'Opponent']).size().reset_index(name='TotalOpponentShots')
               
                       
                
                #st.dataframe(shooting_summary_team)
                #st.dataframe(shooting_summary_opponent)
                
                # Merge the scoring and shooting data for Stevenson and Opponent
                game_summary = pd.merge(
                    team_scoring[['GameDate', 'Team', 'Opponent']].drop_duplicates(),
                    shooting_summary_team[['GameDate', 'TotalStevensonShots']],
                    on='GameDate',
                    how='left'
                )

                game_summary = pd.merge(
                    game_summary,
                    shooting_summary_opponent[['GameDate', 'TotalOpponentShots']],
                    on='GameDate',
                    how='left'
                )

                # Fill NaN values with 0 for games without shooting data
                game_summary['TotalShots'] = game_summary['TotalStevensonShots'].fillna(0)
                game_summary['TotalOpponentShots'] = game_summary['TotalOpponentShots'].fillna(0)

                # Sort by GameDate for better readability
                game_summary = game_summary.sort_values(by='GameDate')
                
                
                #st.dataframe(game_summary)


                # Create the bar chart
                fig = go.Figure(data=[
                    go.Bar(
                        name='Stevenson',
                        x=game_summary['GameDate'],
                        y=game_summary['TotalStevensonShots'],
                        marker_color='rgb(41,77,46)',
                        hovertext=['Stevenson' for _ in range(len(game_summary))],  # Show "Stevenson" on hover
                        hoverinfo='text+y'  # Show the hovertext and y-value (shots)
                    ),
                    go.Bar(
                        name='Opponent',
                        x=game_summary['GameDate'],
                        y=game_summary['TotalOpponentShots'],
                        hovertext=game_summary['Opponent'],  # Show opponent team name on hover
                        hoverinfo='text+y'  # Show the hovertext and y-value (shots)
                    )
                ])

                # Change the bar mode to group
                fig.update_layout(barmode='group', title="Shots by Stevenson and Opponent by Game", xaxis_title="Game Date", yaxis_title="Total Shots", xaxis={'type': 'category'} )

                # Display the bar chart
                st.plotly_chart(fig, use_container_width=True)


                # Add a horizontal line
                st.markdown("<hr>", unsafe_allow_html=True)



                # Filter the data for the selected team and opponents
                team_shooting = final_shots_df[final_shots_df['Team'] == selected_team]
                opponent_shooting = final_shots_df[final_shots_df['Opponent'] == selected_team]

                # Dropdown menu for selecting the view type
                view_type = st.selectbox("View by", ["Total", "By Game"])

                if view_type == "Total":
                    
                    # Aggregate shooting data by game for Stevenson
                    position_summary_team = team_shooting[team_shooting['ShootingTeam'] == 'Stevenson'].groupby([ 'Team','ShootZone']).size().reset_index(name='TotalStevensonShots')

                    # Aggregate shooting data by game for Opponents
                    # Assuming 'final_shots_df' should be 'team_shooting', as 'final_shots_df' is not previously defined
                    position_summary_opponent = team_shooting[team_shooting['ShootingTeam'] != 'Stevenson'].groupby(['ShootZone']).size().reset_index(name='TotalOpponentShots')
                    
                    #st.dataframe(position_summary_team)
                    #st.dataframe(position_summary_opponent)
                    

                    # Create the bar chart
                    fig = go.Figure(data=[
                        go.Bar(
                            name='Stevenson',
                            x=position_summary_team['ShootZone'],
                            y=position_summary_team['TotalStevensonShots'],
                            marker_color='rgb(41,77,46)',
                            hovertext=position_summary_team['ShootZone'],  # Show shooting position on hover
                            hoverinfo='text+y'  # Show the hovertext and y-value (total shots)
                        ),
                        go.Bar(
                            name='Opponent',
                            x=position_summary_opponent['ShootZone'],
                            y=position_summary_opponent['TotalOpponentShots'],
                            hovertext=position_summary_opponent['ShootZone'],  # Show shooting position on hover
                            hoverinfo='text+y',  # Show the hovertext and y-value (total shots)
                            marker_color='rgb(204,36,29)'  # A different color for the opponent
                        )
                    ])

                    fig.update_layout(barmode='group', title="Total Shots by Shooting Position for Stevenson and Opponent", xaxis_title="Shooting Position", yaxis_title="Total Shots")

                else:
                    game_position_summary_team = team_shooting[team_shooting['ShootingTeam'] == 'Stevenson'].groupby(['GameDate', 'Team', 'Opponent','ShootZone']).size().reset_index(name='TotalStevensonShots')

                    # Aggregate shooting data by game for Opponents
                    # Assuming 'final_shots_df' should be 'team_shooting', as 'final_shots_df' is not previously defined
                    game_position_summary_opponent = team_shooting[team_shooting['ShootingTeam'] != 'Stevenson'].groupby(['GameDate', 'Opponent','ShootZone']).size().reset_index(name='TotalOpponentShots')
                    
                    #st.dataframe(game_position_summary_team)
                    #st.dataframe(game_position_summary_opponent)                    
                

                    # Create the bar chart
                    fig = go.Figure()

                    for game_date in game_position_summary_team['GameDate'].unique():
                        game_data_team = game_position_summary_team[game_position_summary_team['GameDate'] == game_date]
                        game_data_opponent = game_position_summary_opponent[game_position_summary_opponent['GameDate'] == game_date]

                        fig.add_trace(go.Bar(
                            name=f'Stevenson - {game_date}',
                            x=game_data_team['ShootZone'],
                            y=game_data_team['TotalStevensonShots'],
                            hovertext=game_data_team['GameDate'],  # Show shooting position on hover
                            hoverinfo='text+y',  # Show the hovertext and y-value (shots)
                            marker_color='rgb(41,77,46)'
                        ))

                        fig.add_trace(go.Bar(
                            name=f'Opponent - {game_date}',
                            x=game_data_opponent['ShootZone'],
                            y=game_data_opponent['TotalOpponentShots'],
                            hovertext=game_data_opponent['GameDate'],  # Show shooting position on hover
                            hoverinfo='text+y',  # Show the hovertext and y-value (shots)
                            marker_color='rgb(204,36,29)'  # A different color for the opponent
                        ))

                    fig.update_layout(barmode='group', title="Shots by Shooting Position and Game for Stevenson and Opponent", xaxis_title="Shooting Position", yaxis_title="Total Shots")

                # Display the bar chart
                st.plotly_chart(fig, use_container_width=True)


                # Add a horizontal line
                st.markdown("<hr>", unsafe_allow_html=True)
                
                
                #st.dataframe(team_shooting.set_index('JerseyNumber'))
                
                
                # Group by jersey number and name, then count scores
                shots_counts = team_shooting.groupby(['JerseyNumber', 'Team','FirstName','LastName','Position']).size().reset_index(name='TotalShots')
                
                # Merging player counts with roster to include player names
                #scored_players = pd.merge(score_counts, roster_df, on='JerseyNumber', how='left')
                

                # Sort the scores in descending order
                sorted_shots = shots_counts.sort_values(by='TotalShots', ascending=False)
                

                st.subheader("Sorted Shots by Player for Stevenson")
                st.dataframe(sorted_shots.set_index('JerseyNumber'), width=650)
                
                # Add a horizontal line
                st.markdown("<hr>", unsafe_allow_html=True)
                
                
                
    
    
    if metric == "Penalties":      
        
        if selected_opponent != "All":
                team_penalties = final_penalties_df[(final_penalties_df['Team'] == selected_team) & (final_penalties_df['Opponent'] == selected_opponent)]
                opponent_penalties = final_penalties_df[(final_penalties_df['Team'] == selected_team) & (final_penalties_df['Opponent'] == selected_opponent)]

                
        else:
                temp_team_penalties = final_penalties_df[final_penalties_df['Team'] == selected_team]  
                team_penalties = final_penalties_df[final_penalties_df['Team'] == selected_team]
                opponent_penalties = final_penalties_df[final_penalties_df['Opponent'] == selected_team]          
        
      
        
        if team_penalties.empty:
                st.subheader(f"No Penalties Data for {selected_team}")
        else:

                # Assuming 'final_penalties_df' is your DataFrame containing the penalties data

                # Filter the data for the selected team and opponents
                #team_penalties = final_penalties_df[final_penalties_df['Team'] == selected_team]
                #opponent_penalties = final_penalties_df[final_penalties_df['Opponent'] == selected_team]

                # Dropdown menu for selecting the view type
                view_type = st.selectbox("View by", ["Total", "By Game"])

                if view_type == "Total":                         
                    penalty_summary_team = team_penalties[team_penalties['PenaltyTeam'] == 'Stevenson'].groupby(['PenaltyCode']).size().reset_index(name='TotalStevensonPenalties')

                    # Aggregate shooting data by game for Opponents
                    # Assuming 'final_shots_df' should be 'team_shooting', as 'final_shots_df' is not previously defined
                    penalty_summary_opponent = team_penalties[team_penalties['PenaltyTeam'] != 'Stevenson'].groupby(['PenaltyCode']).size().reset_index(name='TotalOpponentPenalties')

                              
                    #st.dataframe(penalty_summary_team)
                    #st.dataframe(penalty_summary_opponent)
                    

                    # Create the bar chart
                    fig = go.Figure(data=[
                        go.Bar(
                            name='Stevenson',
                            x=penalty_summary_team['PenaltyCode'],
                            y=penalty_summary_team['TotalStevensonPenalties'],
                            marker_color='rgb(41,77,46)',
                            hovertext=penalty_summary_team['PenaltyCode'],  # Show penalty code on hover
                            hoverinfo='text+y'  # Show the hovertext and y-value (total penalties)
                        ),
                        go.Bar(
                            name='Opponent',
                            x=penalty_summary_opponent['PenaltyCode'],
                            y=penalty_summary_opponent['TotalOpponentPenalties'],
                            hovertext=penalty_summary_opponent['PenaltyCode'],  # Show penalty code on hover
                            hoverinfo='text+y',  # Show the hovertext and y-value (total penalties)
                            marker_color='rgb(204,36,29)'  # A different color for the opponent
                        )
                    ])

                    fig.update_layout(barmode='group', title="Total Penalties by Penalty Code for Stevenson and Opponent", xaxis_title="Penalty Code", yaxis_title="Total Penalties")

                else:
                    # Aggregate penalties by PenaltyCode and game for Stevenson and Opponents
                    #game_penalty_summary_team = team_penalties.groupby(['GameDate', 'PenaltyCode']).size().reset_index(name='TotalPenalties')
                    #game_penalty_summary_opponent = opponent_penalties.groupby(['GameDate', 'PenaltyCode']).size().reset_index(name='TotalPenalties')
                    
                    
                    game_penalty_summary_team = team_penalties[team_penalties['PenaltyTeam'] == 'Stevenson'].groupby(['GameDate', 'Team', 'Opponent','PenaltyCode']).size().reset_index(name='TotalStevensonPenalties')

                    game_penalty_summary_opponent = team_penalties[team_penalties['PenaltyTeam'] != 'Stevenson'].groupby(['GameDate', 'Opponent','PenaltyCode']).size().reset_index(name='TotalOpponentPenalties')
                    
                    
                    
                    

                    # Create the bar chart
                    fig = go.Figure()

                    for game_date in game_penalty_summary_team['GameDate'].unique():
                        game_data_team = game_penalty_summary_team[game_penalty_summary_team['GameDate'] == game_date]
                        game_data_opponent = game_penalty_summary_opponent[game_penalty_summary_opponent['GameDate'] == game_date]

                        fig.add_trace(go.Bar(
                            name=f'Stevenson - {game_date}',
                            x=game_data_team['PenaltyCode'],
                            y=game_data_team['TotalStevensonPenalties'],
                            hovertext=game_data_team['GameDate'],  # Show penalty code on hover
                            hoverinfo='text+y',  # Show the hovertext and y-value (penalties)
                            marker_color='rgb(41,77,46)'
                        ))

                        fig.add_trace(go.Bar(
                            name=f'Opponent - {game_date}',
                            x=game_data_opponent['PenaltyCode'],
                            y=game_data_opponent['TotalOpponentPenalties'],
                            hovertext=game_data_opponent['GameDate'],  # Show penalty code on hover
                            hoverinfo='text+y',  # Show the hovertext and y-value (penalties)
                            marker_color='rgb(204,36,29)'  # A different color for the opponent
                        ))

                    fig.update_layout(barmode='group', title="Penalties by Penalty Code and Game for Stevenson and Opponent", xaxis_title="Penalty Code", yaxis_title="Total Penalties")

                # Display the bar chart
                st.plotly_chart(fig, use_container_width=True)

                
            
                # Add a horizontal line
                st.markdown("<hr>", unsafe_allow_html=True)
                
                #st.dataframe(team_penalties.set_index('JerseyNumber'))
                
                
                # Group by jersey number and name, then count scores
                penalties_counts = team_penalties.groupby(['JerseyNumber', 'Team','FirstName','LastName','Position']).size().reset_index(name='TotalNumPenalties')
                
                # Merging player counts with roster to include player names
                #scored_players = pd.merge(score_counts, roster_df, on='JerseyNumber', how='left')
                

                # Sort the scores in descending order
                sorted_penalties = penalties_counts.sort_values(by='TotalNumPenalties', ascending=False)
                

                st.subheader("Sorted Penalties by Player for Stevenson")
                st.dataframe(sorted_penalties.set_index('JerseyNumber'), width=650)
                
                # Add a horizontal line
                st.markdown("<hr>", unsafe_allow_html=True)
            
            
            
    if metric == "Faceoff":
        #faceoff_outcomes = final_faceoff_df[final_faceoff_df['Team'] == selected_team]    
        
        if selected_opponent != "All":
                faceoff_stevenson = faceoff_df[(faceoff_df['Team'] == selected_team) & (faceoff_df['Opponent'] == selected_opponent)]
                
        else:
                faceoff_stevenson = faceoff_df[faceoff_df['Team'] == selected_team]
        

        
        #st.dataframe(faceoff_stevenson.set_index('JerseyNumber'), width=650)
        
        
        if faceoff_stevenson.empty:
                st.subheader(f"No Faceoff Data for {selected_team}")
        else:    
            
            
            
                # Perform the merge for 'Stevenson' team
                faceoff_merged_stevenson = pd.merge(
                    faceoff_stevenson,
                    roster_df[['Team', 'JerseyNumber', 'FirstName', 'LastName', 'Position']],
                    how='left',
                    left_on=['Team', 'JerseyNumber'],
                    right_on=['Team', 'JerseyNumber']
                )                  

                
                
                #st.dataframe(faceoff_merged_stevenson.set_index('JerseyNumber'), width=650)

                
                summary = faceoff_merged_stevenson.groupby(['JerseyNumber', 'FirstName', 'LastName', 'Position']).agg(
                    total_wins=('Win', 'sum'),
                    total_losses=('Lose', 'sum')
                ).reset_index()
                
                
                #st.dataframe(summary.set_index('JerseyNumber'), width=650)
                

                # Calculating win rate
                summary['win_rate'] = (summary['total_wins'] / (summary['total_wins'] + summary['total_losses'])) * 100
                summary['win_rate'] = summary['win_rate'].round(1)  # rounding to one decimal
                summary = summary.sort_values(by='win_rate', ascending=False).reset_index(drop=True)
                
                summary['win_rate'] = summary['win_rate'].astype(str) + '%'


                # Calculate total unique games played
                st.dataframe(summary.set_index('JerseyNumber'), width=650)
                #total_faceoff = faceoff_outcomes[['GameDate', 'Team', 'Opponent']].drop_duplicates().shape[0]    

    
    
    
elif view_by == "Player":
    
    team_players = roster_df[roster_df['Team'] == selected_team]
    selected_player = st.sidebar.selectbox("Select Player", team_players['LastName'] + ", " + team_players['FirstName'])

    
    last_name, first_name = selected_player.split(", ")
    player_info = team_players[(team_players['LastName'] == last_name) & (team_players['FirstName'] == first_name)]

    # Retrieving the JerseyNumber
    jersey_number = player_info['JerseyNumber'].values[0]  # Ensure there is at least one match before indexing

     
    #st.dataframe(team_players.set_index('JerseyNumber'), width=650)
    #st.write("selected_player",selected_player) 
    #st.write(jersey_number)  
    
    
    player_shots = final_shots_df[(final_shots_df['LastName'] + ", " + final_shots_df['FirstName']) == selected_player]
    player_scores = final_scoring_df[(final_scoring_df['LastName'] + ", " + final_scoring_df['FirstName']) == selected_player]
    player_penalties = final_penalties_df[(final_penalties_df['LastName'] + ", " + final_penalties_df['FirstName']) == selected_player]    

         
    #st.dataframe(player_shots.set_index('JerseyNumber'), width=650)
    #st.dataframe(player_scores.set_index('JerseyNumber'), width=650)
    #st.dataframe(player_penalties.set_index('JerseyNumber'), width=650)

    
    if player_shots.empty & player_scores.empty & player_penalties.empty:
            st.subheader(f"No Data for {selected_player}")
    else:
            st.subheader(f"Statistics for {selected_player}")
            
            #st.dataframe(player_shots, width=650)
            shots_counts_player = player_shots.groupby(['GameDate','Opponent','JerseyNumber']).size().reset_index(name='TotalShots')
            
            
            # Sort the scores in descending order
            shots_counts_player = shots_counts_player.sort_values(by='GameDate', ascending=False)


  
    
    
            score_counts_player = player_scores.groupby(['GameDate','Opponent','JerseyNumber']).size().reset_index(name='TotalScores')
            
            
            # Sort the scores in descending order
            score_counts_player = score_counts_player.sort_values(by='GameDate', ascending=False)

            
           
            
            
            team_outcomes = final_scoring_df[final_scoring_df['Team'] == selected_team]
            
            # Selecting the required columns and filtering by 'ScoringTeam'
            #assistants_player1 = team_outcomes[team_outcomes['ScoringTeam'] == 'Stevenson'][['GameDate', 'Team', 'Opponent', 'Assistant_1']]
            
            assistants_player1 = team_outcomes[
    (team_outcomes['ScoringTeam'] == 'Stevenson') &
    (team_outcomes['Assistant_1'] == jersey_number)
][['GameDate', 'Team', 'Opponent', 'Assistant_1']]

            # Renaming 'Assistant_1' to 'JerseyNumber'
            assistants_player1 = assistants_player1.rename(columns={'Assistant_1': 'JerseyNumber'})
                
            # Selecting the required columns and filtering by 'ScoringTeam'
            #assistants_player2 = team_outcomes[team_outcomes['ScoringTeam'] == 'Stevenson'][['GameDate', 'Team', 'Opponent', 'Assistant_2']]
            
            assistants_player2 = team_outcomes[
    (team_outcomes['ScoringTeam'] == 'Stevenson') &
    (team_outcomes['Assistant_1'] == jersey_number)
][['GameDate', 'Team', 'Opponent', 'Assistant_2']]

            # Renaming 'Assistant_1' to 'JerseyNumber'
            assistants_player2 = assistants_player2.rename(columns={'Assistant_2': 'JerseyNumber'})                
                
      
            assistants_player = pd.concat([assistants_player1, assistants_player2], axis=0)

            # Reset the index after concatenation, if needed
            assistants_player = assistants_player.reset_index(drop=True)
            assistants_player = assistants_player.dropna(subset=['JerseyNumber'])
                
            
            #st.dataframe(assistants_player.set_index('JerseyNumber'), width=600)
            #st.write(assistants_player.columns)
            
            # Counting the number of records for each JerseyNumber
            player_assistants_counts = assistants_player.groupby(['JerseyNumber', 'GameDate','Opponent']).size().reset_index(name='TotalAssistants')

            
            #st.dataframe(player_assistants_counts.set_index('JerseyNumber'), width=600)
            
    
    
    
    
    
            penaltys_counts_player = player_penalties.groupby(['GameDate','Opponent','JerseyNumber']).size().reset_index(name='TotalPenalties')
            
            
            # Sort the scores in descending order
            penaltys_counts_player = penaltys_counts_player.sort_values(by='GameDate', ascending=False)

    
    
            # Merge the DataFrames on 'JerseyNumber', 'GameDate', and 'Opponent', keeping all records
            result = score_counts_player.merge(shots_counts_player, on=['JerseyNumber', 'GameDate', 'Opponent'], how='outer')
            result = result.merge(penaltys_counts_player, on=['JerseyNumber', 'GameDate', 'Opponent'], how='outer')
            result = result.merge(player_assistants_counts, on=['JerseyNumber', 'GameDate', 'Opponent'], how='outer')

            # Replace null values with 0
            result.fillna(0, inplace=True)

    
            result = result.sort_values(by='GameDate', ascending=False)
        
        
            total_scores = result['TotalScores'].sum()
            total_assistants = result['TotalAssistants'].sum()
            total_shots = result['TotalShots'].sum()
            total_penalties = result['TotalPenalties'].sum()
            
            score_rate = (total_scores / total_shots) * 100 if total_shots > 0 else 0
        
            
            # Create columns for the summary stats
            col1, col2, col3, col4, col5 = st.columns(5)
            col1.metric("Total Scores", int(total_scores))
            col2.metric("Total Assistants", int(total_assistants))
            col3.metric("Total Shots", int(total_shots))
            col4.metric("Scoring Rate", f"{score_rate:.1f}%")
            col5.metric("Total Penalties", int(total_penalties))
            
            
            st.markdown("<hr>", unsafe_allow_html=True)
            
        
            st.dataframe(result.set_index('JerseyNumber'), width=900)
      
        
    st.markdown("<hr>", unsafe_allow_html=True)
    


    
    

elif view_by == "Game":
    
    
    team_games = scoring_df[scoring_df['Team'] == selected_team]
    team_games['FormattedDate'] = pd.to_datetime(team_games['GameDate']).dt.strftime('%Y-%m-%d')
    
    #selected_game = st.sidebar.selectbox("Select Game Date", team_games['GameDate'].unique())
    selected_game = st.sidebar.selectbox("Select Game Date", team_games['FormattedDate'].unique())


    #original_game_date = team_games[team_games['FormattedDate'] == selected_game]['GameDate'].iloc[0]
    #st.write(f"Selected Game Date: {original_game_date}")

    
    
    if team_games.empty:
            st.subheader(f"No Game Data for {selected_team}")
    else:

            metric = st.radio("Metric", ["Shots", "Penalties", "Game Outcomes"])

            if metric == "Shots":
                game_shooting = final_shots_df[final_shots_df['GameDate'] == selected_game]
                st.subheader(f"Shooting Data for {selected_game}")
                sns.barplot(data=game_shooting, x='Period', y='ShootZone', hue='Team')
                st.pyplot()

            elif metric == "Penalties":
                game_penalties = final_penalties_df[final_penalties_df['GameDate'] == selected_game]
                st.subheader(f"Penalties for {selected_game}")
                penalties = game_penalties.groupby('Period')['PenaltyMins'].sum()
                st.bar_chart(penalties)

            elif metric == "Game Outcomes":
                game_outcomes = final_scoring_df[final_scoring_df['GameDate'] == selected_game]
                outcomes = game_outcomes.groupby('Team')['Win'].first()  # Assuming 'Win' is a binary column
                st.subheader(f"Game Outcomes for {selected_game}")
                st.line_chart(outcomes)


