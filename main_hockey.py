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



#st.set_option('deprecation.showPyplotGlobalUse', False)


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




# Load your data
#file_path = 'Stevenson_Hockey.xlsx'
data = pd.ExcelFile('Stevenson_Hockey.xlsx')


# Load the sheets into separate DataFrames
roster_df = pd.read_excel(data, sheet_name='Roster')
scoring_df = pd.read_excel(data, sheet_name='Scoring')
penalties_df = pd.read_excel(data, sheet_name='Penalties')
shooting_df = pd.read_excel(data, sheet_name='Shooting')



#######################
# Sidebar
with st.sidebar:
    st.subheader('Stevenson Hockey Dashboard')
    
    team_list = list(roster_df.Team.unique())[::-1]
    
    selected_team = st.selectbox('Select a team', team_list)
    df_selected_team = roster_df[roster_df.Team == selected_team]
    df_selected_team_sorted = df_selected_team.sort_values(by="JerseyNumber", ascending=False)


    # Sidebar options
    st.sidebar.title("Select Options")
    view_by = st.sidebar.radio("View By", ["Team", "Player", "Game"])
    
    

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









shooting_stevenson = shooting_df[shooting_df['ShootingTeam'] == 'Stevenson']

# Perform the merge for 'Stevenson' team
shooting_merged_stevenson = pd.merge(
    shooting_stevenson,
    roster_df[['Team', 'JerseyNumber', 'FirstName', 'LastName', 'Position']],
    how='left',
    left_on=['Team', 'JerseyNumber'],
    right_on=['Team', 'JerseyNumber']
)

# Filter out non-Stevenson shooting records and concatenate them back with the merged Stevenson data
shooting_non_stevenson = shooting_df[shooting_df['ShootingTeam'] != 'Stevenson']

# Combine the Stevenson merged shooting data with non-Stevenson shooting data
final_shooting_df = pd.concat([shooting_merged_stevenson, shooting_non_stevenson], ignore_index=True)


# Convert the 'GameDate' to a string format (YYYY-MM-DD)
final_shooting_df['FormattedDate'] = pd.to_datetime(final_shooting_df['GameDate']).dt.strftime('%Y-%m-%d')

# Optionally, if you want to replace the original 'GameDate' column:
final_shooting_df['GameDate'] = final_shooting_df['FormattedDate']
final_shooting_df.drop(columns=['FormattedDate'], inplace=True)





st.subheader("Hockey Data Analysis")

# Add a horizontal line
st.markdown("<hr>", unsafe_allow_html=True)
#metric = st.radio("Metric", ["Shooting", "Penalties", "Game Outcomes"])



if view_by == "Team":
    selected_team = st.sidebar.selectbox("Select Team", roster_df['Team'].unique())
    
    #metric = st.radio("Metric", ["Shots", "Penalties", "Game Outcomes"])
    
    metric = st.radio("Metric", ["Game Outcomes", "Shots", "Penalties"])
    
    # Add a horizontal line
    st.markdown("<hr>", unsafe_allow_html=True)
    
    if metric == "Game Outcomes":
 
        team_outcomes = final_scoring_df[final_scoring_df['Team'] == selected_team]

        if team_outcomes.empty:
                st.subheader(f"No Game Data for {selected_team}")
        else:    
                # Calculate total unique games played
                total_games = team_outcomes[['GameDate', 'Team', 'Opponent']].drop_duplicates().shape[0]

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

                # Create hovertext that shows "Stevenson" for Stevenson bars and the opponent's name for the opponent bars
                stevenson_hovertext = ['Stevenson' for _ in range(len(scores_data))]
                opponent_hovertext = scores_data['Opponent']

                fig = go.Figure(data=[
                    go.Bar(
                        name='Stevenson',
                        x=scores_data['GameDate'],
                        y=scores_data['ScoreStevenson'],
                        marker_color='rgb(41,77,46)',
                        hovertext=stevenson_hovertext,  # Show "Stevenson" on hover
                        hoverinfo='text+y'  # Show the hovertext and y-value (score)
                    ),
                    go.Bar(
                        name='Opponent',
                        x=scores_data['GameDate'],
                        y=scores_data['ScoreOpponent'],
                        hovertext=opponent_hovertext,  # Show opponent team name on hover
                        hoverinfo='text+y'  # Show the hovertext and y-value (score)
                    )
                ])

                # Change the bar mode to group
                fig.update_layout(barmode='group', title="Scores by Stevenson and Opponent by Game", xaxis_title="Game Date", yaxis_title="Scores")

                # Display the bar chart
                st.plotly_chart(fig, use_container_width=True)

                

    
    if metric == "Shots":   
        team_shooting = final_shooting_df[final_shooting_df['Team'] == selected_team]

        if team_shooting.empty:
                st.subheader(f"No Shooting Data for {selected_team}")
        else:


                # Filter the data for the selected team
                team_scoring = final_scoring_df[final_scoring_df['Team'] == selected_team]
                team_shooting = final_shooting_df[final_shooting_df['Team'] == selected_team]

                # Aggregate shooting data by game for Stevenson
                shooting_summary_team = team_shooting.groupby(['GameDate', 'Team', 'Opponent']).size().reset_index(name='TotalShots')

                # Aggregate shooting data by game for Opponent
                shooting_summary_opponent = final_shooting_df.groupby(['GameDate', 'Opponent']).size().reset_index(name='TotalOpponentShots')

                # Merge the scoring and shooting data for Stevenson and Opponent
                game_summary = pd.merge(
                    team_scoring[['GameDate', 'Team', 'Opponent']].drop_duplicates(),
                    shooting_summary_team[['GameDate', 'TotalShots']],
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
                game_summary['TotalShots'] = game_summary['TotalShots'].fillna(0)
                game_summary['TotalOpponentShots'] = game_summary['TotalOpponentShots'].fillna(0)

                # Sort by GameDate for better readability
                game_summary = game_summary.sort_values(by='GameDate')

                # Create the bar chart
                fig = go.Figure(data=[
                    go.Bar(
                        name='Stevenson',
                        x=game_summary['GameDate'],
                        y=game_summary['TotalShots'],
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
                fig.update_layout(barmode='group', title="Shots by Stevenson and Opponent by Game", xaxis_title="Game Date", yaxis_title="Total Shots")

                # Display the bar chart
                st.plotly_chart(fig, use_container_width=True)






                # Filter the data for the selected team and opponents
                team_shooting = final_shooting_df[final_shooting_df['Team'] == selected_team]
                opponent_shooting = final_shooting_df[final_shooting_df['Opponent'] == selected_team]

                # Dropdown menu for selecting the view type
                view_type = st.selectbox("View by", ["Total", "By Game"])

                if view_type == "Total":
                    # Aggregate total shots by position for Stevenson and Opponents for the entire season
                    position_summary_team = team_shooting.groupby('ShootZone').size().reset_index(name='TotalShots')
                    position_summary_opponent = opponent_shooting.groupby('ShootZone').size().reset_index(name='TotalShots')

                    # Create the bar chart
                    fig = go.Figure(data=[
                        go.Bar(
                            name='Stevenson',
                            x=position_summary_team['ShootZone'],
                            y=position_summary_team['TotalShots'],
                            marker_color='rgb(41,77,46)',
                            hovertext=position_summary_team['ShootZone'],  # Show shooting position on hover
                            hoverinfo='text+y'  # Show the hovertext and y-value (total shots)
                        ),
                        go.Bar(
                            name='Opponent',
                            x=position_summary_opponent['ShootZone'],
                            y=position_summary_opponent['TotalShots'],
                            hovertext=position_summary_opponent['ShootZone'],  # Show shooting position on hover
                            hoverinfo='text+y',  # Show the hovertext and y-value (total shots)
                            marker_color='rgb(204,36,29)'  # A different color for the opponent
                        )
                    ])

                    fig.update_layout(barmode='group', title="Total Shots by Shooting Position for Stevenson and Opponent", xaxis_title="Shooting Position", yaxis_title="Total Shots")

                else:
                    # Aggregate shots by position and game for Stevenson and Opponents
                    game_position_summary_team = team_shooting.groupby(['GameDate', 'ShootZone']).size().reset_index(name='TotalShots')
                    game_position_summary_opponent = opponent_shooting.groupby(['GameDate', 'ShootZone']).size().reset_index(name='TotalShots')

                    # Create the bar chart
                    fig = go.Figure()

                    for game_date in game_position_summary_team['GameDate'].unique():
                        game_data_team = game_position_summary_team[game_position_summary_team['GameDate'] == game_date]
                        game_data_opponent = game_position_summary_opponent[game_position_summary_opponent['GameDate'] == game_date]

                        fig.add_trace(go.Bar(
                            name=f'Stevenson - {game_date}',
                            x=game_data_team['ShootZone'],
                            y=game_data_team['TotalShots'],
                            hovertext=game_data_team['ShootZone'],  # Show shooting position on hover
                            hoverinfo='text+y',  # Show the hovertext and y-value (shots)
                            marker_color='rgb(41,77,46)'
                        ))

                        fig.add_trace(go.Bar(
                            name=f'Opponent - {game_date}',
                            x=game_data_opponent['ShootZone'],
                            y=game_data_opponent['TotalShots'],
                            hovertext=game_data_opponent['ShootZone'],  # Show shooting position on hover
                            hoverinfo='text+y',  # Show the hovertext and y-value (shots)
                            marker_color='rgb(204,36,29)'  # A different color for the opponent
                        ))

                    fig.update_layout(barmode='group', title="Shots by Shooting Position and Game for Stevenson and Opponent", xaxis_title="Shooting Position", yaxis_title="Total Shots")

                # Display the bar chart
                st.plotly_chart(fig, use_container_width=True)





    
    
    
    
    if metric == "Penalties":      
        team_penalties = final_penalties_df[final_penalties_df['Team'] == selected_team]


        if team_penalties.empty:
                st.subheader(f"No Penalties Data for {selected_team}")
        else:

                # Assuming 'final_penalties_df' is your DataFrame containing the penalties data

                # Filter the data for the selected team and opponents
                team_penalties = final_penalties_df[final_penalties_df['Team'] == selected_team]
                opponent_penalties = final_penalties_df[final_penalties_df['Opponent'] == selected_team]

                # Dropdown menu for selecting the view type
                view_type = st.selectbox("View by", ["Total", "By Game"])

                if view_type == "Total":
                    # Aggregate total penalties by PenaltyCode for Stevenson and Opponents for the entire season
                    penalty_summary_team = team_penalties.groupby('PenaltyCode').size().reset_index(name='TotalPenalties')
                    penalty_summary_opponent = opponent_penalties.groupby('PenaltyCode').size().reset_index(name='TotalPenalties')

                    # Create the bar chart
                    fig = go.Figure(data=[
                        go.Bar(
                            name='Stevenson',
                            x=penalty_summary_team['PenaltyCode'],
                            y=penalty_summary_team['TotalPenalties'],
                            marker_color='rgb(41,77,46)',
                            hovertext=penalty_summary_team['PenaltyCode'],  # Show penalty code on hover
                            hoverinfo='text+y'  # Show the hovertext and y-value (total penalties)
                        ),
                        go.Bar(
                            name='Opponent',
                            x=penalty_summary_opponent['PenaltyCode'],
                            y=penalty_summary_opponent['TotalPenalties'],
                            hovertext=penalty_summary_opponent['PenaltyCode'],  # Show penalty code on hover
                            hoverinfo='text+y',  # Show the hovertext and y-value (total penalties)
                            marker_color='rgb(204,36,29)'  # A different color for the opponent
                        )
                    ])

                    fig.update_layout(barmode='group', title="Total Penalties by Penalty Code for Stevenson and Opponent", xaxis_title="Penalty Code", yaxis_title="Total Penalties")

                else:
                    # Aggregate penalties by PenaltyCode and game for Stevenson and Opponents
                    game_penalty_summary_team = team_penalties.groupby(['GameDate', 'PenaltyCode']).size().reset_index(name='TotalPenalties')
                    game_penalty_summary_opponent = opponent_penalties.groupby(['GameDate', 'PenaltyCode']).size().reset_index(name='TotalPenalties')

                    # Create the bar chart
                    fig = go.Figure()

                    for game_date in game_penalty_summary_team['GameDate'].unique():
                        game_data_team = game_penalty_summary_team[game_penalty_summary_team['GameDate'] == game_date]
                        game_data_opponent = game_penalty_summary_opponent[game_penalty_summary_opponent['GameDate'] == game_date]

                        fig.add_trace(go.Bar(
                            name=f'Stevenson - {game_date}',
                            x=game_data_team['PenaltyCode'],
                            y=game_data_team['TotalPenalties'],
                            hovertext=game_data_team['PenaltyCode'],  # Show penalty code on hover
                            hoverinfo='text+y',  # Show the hovertext and y-value (penalties)
                            marker_color='rgb(41,77,46)'
                        ))

                        fig.add_trace(go.Bar(
                            name=f'Opponent - {game_date}',
                            x=game_data_opponent['PenaltyCode'],
                            y=game_data_opponent['TotalPenalties'],
                            hovertext=game_data_opponent['PenaltyCode'],  # Show penalty code on hover
                            hoverinfo='text+y',  # Show the hovertext and y-value (penalties)
                            marker_color='rgb(204,36,29)'  # A different color for the opponent
                        ))

                    fig.update_layout(barmode='group', title="Penalties by Penalty Code and Game for Stevenson and Opponent", xaxis_title="Penalty Code", yaxis_title="Total Penalties")

                # Display the bar chart
                st.plotly_chart(fig, use_container_width=True)

            
            
    

    
    
    
elif view_by == "Player":
    
    team_players = roster_df[roster_df['Team'] == selected_team]
    selected_player = st.sidebar.selectbox("Select Player", team_players['LastName'] + ", " + team_players['FirstName'])
   

    
    metric = st.radio("Metric", ["Scores", "Shots", "Penalties"])
    
    if metric == "Shots":
        player_shooting = final_shooting_df[(final_shooting_df['LastName'] + ", " + final_shooting_df['FirstName']) == selected_player]
        
        
        if player_shooting.empty:
            st.subheader(f"No Shooting Data for {selected_player}")
        else:
            st.subheader(f"Shooting Data for {selected_player}")
            sns.barplot(data=player_shooting, x='Period', y='ShootZone')
            st.pyplot()
            
            
        # Add a horizontal line
        st.markdown("<hr>", unsafe_allow_html=True)        
        
        
    elif metric == "Scores":     


        # Calculate total scores by player across all games
        total_scores_by_player = final_scoring_df.groupby(['FirstName', 'LastName'])['ScoreStevenson'].sum().reset_index()
        total_scores_by_player.rename(columns={'ScoreStevenson': 'TotalScores'}, inplace=True)

        # Calculate scores by player for each game
        scores_by_game = final_scoring_df.groupby(['GameDate', 'FirstName', 'LastName'])['ScoreStevenson'].sum().reset_index()
        scores_by_game.rename(columns={'ScoreStevenson': 'ScoresByGame'}, inplace=True)

        # Display the results
        st.write("Total Scores by Player:")
        st.write(total_scores_by_player)

        st.write("Scores by Player for Each Game:")
        st.write(scores_by_game)


        
        
        
        
        
        
        
        
        
        
        
        # Add a horizontal line
        st.markdown("<hr>", unsafe_allow_html=True)   
    
        
    elif metric == "Penalties":
        player_penalties = final_penalties_df[(final_penalties_df['LastName'] + ", " + final_penalties_df['FirstName']) == selected_player]
        st.subheader(f"Penalties for {selected_player}")
        penalties = player_penalties.groupby('Period')['PenaltyMins'].sum()
        st.bar_chart(penalties)

    elif metric == "Game Outcomes":
        player_outcomes = final_scoring_df[(final_scoring_df['LastName'] + ", " + final_scoring_df['FirstName']) == selected_player]
        outcomes = player_outcomes.groupby('GameDate')['Win'].first()  # Assuming 'Win' is a binary column
        st.subheader(f"Game Outcomes for {selected_player}")
        st.line_chart(outcomes)
        
        

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
                game_shooting = final_shooting_df[final_shooting_df['GameDate'] == selected_game]
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



