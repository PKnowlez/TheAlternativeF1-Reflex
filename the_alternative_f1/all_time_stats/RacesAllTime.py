# All Time Race Results

import streamlit as st
import Functions

def RaceStats(NumSeason):
    # Input Variables
    #   NumSeason: the number of seasons that have occurred to date
    col1, col2 = st.columns(2)
    with col1:
        st.subheader('Race Results by Constructor')
        Functions.RacesAllTime(NumSeason,'Team')
    with col2:
        st.subheader('Race Results by Driver')
        Functions.RacesAllTime(NumSeason,'Driver')