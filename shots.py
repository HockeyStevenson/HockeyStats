import numpy as np
import os, sys
from datetime import datetime

sys.path.insert(1, './shared')

import streamlit as st
import pandas as pd

import base64


from streamlit_gsheets import GSheetsConnection

# Create a connection object.
conn = st.connection("gsheets", type=GSheetsConnection)

# Read data from the specific worksheet
df = conn.read(
    worksheet="shots"
)

# Print results.
for row in df.itertuples():
    st.write(f"On {row.GameDate} {row.Team} has a game with {row.Opponent}. {row.JerseyNumber} has a shot from {row.ShootZone}.")





# Placeholder for the data to be saved
data_to_save = []


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
    page_title="Stevenson Hockey Shots Data",
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

#######################


# Sidebar
with st.sidebar:
    st.subheader('Stevenson Hockey Shots Data')
    
    # Select team from roster
    team_list = list(roster_df.Team.unique())[::-1]
    selected_team = st.selectbox('Select a team', team_list)
    
    # Filter and sort the selected team data
    df_selected_team = roster_df[roster_df.Team == selected_team]
    df_selected_team_sorted = df_selected_team.sort_values(by="JerseyNumber", ascending=False)
    unique_jersey_numbers = sorted(df_selected_team_sorted['JerseyNumber'].unique())


    # Add the option to add a new opponent
    opponents = ["New Trier Trevians", "GBN", "GBS"]
    
    # If a new opponent is added, handle the input and update the opponent list
    opponent = st.selectbox("Select Opponent", opponents + ["Add New Opponent..."])

    if opponent == "Add New Opponent...":
        new_opponent = st.text_input("Enter new opponent name")
        if new_opponent:
            opponents.append(new_opponent)  # Dynamically add the new opponent to the list
            opponent = new_opponent  # Update the opponent variable to the new entry
            
            
    # Add game date selection with default to today's date
    game_date = st.date_input("Select Game Date", datetime.today())
            
        
    # Add a radio button to select if Stevenson is home or away
    stevenson_home = st.radio("Is Stevenson the Home Team?", ("Yes", "No"))





# Main area
st.title("Hockey Game Shots Input")


# Function to save data to CSV
def save_data_to_csv():
    if data_to_save:
        df = pd.DataFrame(data_to_save)
        df.to_csv("temp_data.csv", index=False)
        st.success("Data saved successfully!")



# Add a radio button for selecting the period, displayed horizontally
period = st.radio("Select Period", options=["1", "2", "3", "Overtime"], horizontal=True)


# Create two sections: Stevenson Team and Opponent Team, with a vertical line in between
col1, col_mid, col2 = st.columns([10, 1, 10])  # Adjust column width ratios as needed


# Stevenson Team Section
with col1:
    st.header(f"Stevenson Team - Period {period}")
    stevenson_shots = st.slider(f"Number of Shots by Stevenson in Period {period}", min_value=0, max_value=30, value=0)
    
    if stevenson_shots > 0:
        st.subheader(f"Stevenson Shots Details for Period {period}")
        for i in range(stevenson_shots):
            cols = st.columns([2, 2, 1, 1])  # Define column widths
            with cols[0]:
                shoot_zone = st.selectbox(f"Shoot Zone (Shot {i+1})", 
                                          ["Blue Line", "Boards", "Corners", "Defensive Zone", 
                                           "Faceoff Circles", "Faceoff Dots", "Goal Crease", 
                                           "High Slot", "Neutral Zone", "Offensive Zone", "Slot"], 
                                          key=f"stevenson_shoot_zone_{i}")
            with cols[1]:
                jersey_number = st.selectbox(f"Jersey Number (Shot {i+1})", unique_jersey_numbers, key=f"stevenson_jersey_{i}")
            with cols[2]:
                is_powerplay = st.checkbox(f"Is Powerplay (Shot {i+1})", value=False, key=f"stevenson_powerplay_{i}")
            with cols[3]:
                is_goal = st.checkbox(f"Is Goal (Shot {i+1})", value=False, key=f"stevenson_goal_{i}")
            data_to_save.append({
                "GameDate": game_date.strftime('%Y-%m-%d'),
                "Team": selected_team,
                "Opponent": opponent,
                "Period": period,
                "IsPowerplay": is_powerplay,   
                "JerseyNumber": jersey_number,               
                "ShootingTeam": "Stevenson",
                "ShootZone": shoot_zone,
                "IsGoal": is_goal
            })

            
            
# Vertical line separator
with col_mid:
    st.markdown("##")
    st.markdown(".")

            
            
# Opponent Team Section
with col2:
    st.header(f"Opponent Team - Period {period}")
    opponent_shots = st.slider(f"Number of Shots by Opponent in Period {period}", min_value=0, max_value=30, value=0)
    
    if opponent_shots > 0:
        st.subheader(f"Opponent Shots Details for Period {period}")
        for i in range(opponent_shots):
            cols = st.columns([2, 2, 1, 1])  # Define column widths
            with cols[0]:
                shoot_zone = st.selectbox(f"Shoot Zone (Shot {i+1})", 
                                          ["Blue Line", "Boards", "Corners", "Defensive Zone", 
                                           "Faceoff Circles", "Faceoff Dots", "Goal Crease", 
                                           "High Slot", "Neutral Zone", "Offensive Zone", "Slot"], 
                                          key=f"opponent_shoot_zone_{i}")
            with cols[1]:
                jersey_number = st.text_input(f"Jersey Number (Shot {i+1})", value="0", key=f"opponent_jersey_{i}")
            with cols[2]:
                is_powerplay = st.checkbox(f"Is Powerplay (Shot {i+1})", value=False, key=f"opponent_powerplay_{i}")
            with cols[3]:
                is_goal = st.checkbox(f"Is Goal (Shot {i+1})", value=False, key=f"opponent_goal_{i}")
            data_to_save.append({
                "GameDate": game_date.strftime('%Y-%m-%d'),
                "Team": selected_team,
                "Opponent": opponent,
                "Period": period,        
                "IsPowerplay": is_powerplay,
                "JerseyNumber": jersey_number,                
                "ShootingTeam": opponent,
                "ShootZone": shoot_zone,
                "IsGoal": is_goal
            })

# Add a horizontal line
st.markdown("<hr>", unsafe_allow_html=True)  
            
# Add a "SAVE" button to save the data
if st.button("SAVE"):
    save_data_to_csv()
