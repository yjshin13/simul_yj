import streamlit as st
import pandas as pd
import resampled_mvo
from datetime import datetime

def data(file):

    assets = pd.read_excel(file, sheet_name="Daily_price",
                           names=None, dtype={'Date': datetime}, index_col=0, header=4).dropna()

    return assets

file = st.file_uploader("파일_선택(CSV)", type=['xlsx', 'xls', 'csv'])

tickers = ('select', data(file).columns.keys())
number1 = st.number_input('Efficient Frontier Points')
st.write(number1)

number2 = st.number_input('Number of Simulations')
st.write(number2)

number3 = st.number_input('Select Target Return(%)')
st.write(number3)

