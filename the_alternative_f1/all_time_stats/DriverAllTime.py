# This script will almagamte all of the previous season's results for a driver to determine:
#   Total Wins, Second, and Third Place
#   Total Podiums
#   Total Points
# It will provide a table for all of the drivers with all of this information

import streamlit as st
import pandas as pd
import Functions

def DriverStats(season,tORd):
    st.subheader("All Time Driver's Statistics")
    st.markdown('''
                Below summarizes The Alternative's F1 League Driver statistics over the course of Season 1 - Season 
                ''' + str(season) + ".")
    st.markdown('''
                To ensure accuracy, this page is updated at the conclusion of each season, once all points, wins, and podiums are finalized.
                ''')
    Functions.CalculateAllTime(season,tORd)