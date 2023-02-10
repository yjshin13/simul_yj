import streamlit as st
import pandas as pd
import resampled_mvo
from datetime import datetime

number1 = st.number_input('Efficient Frontier Points')
st.write(number1)

number2 = st.number_input('Number of Simulations')
st.write(number2)

number3 = st.number_input('Select Target Return(%)')
st.write(number3)

file = st.file_uploader("파일_선택(CSV)", type=['xlsx', 'xls', 'csv'])
