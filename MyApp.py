import streamlit as st
import pandas as pd
from webSAA import resampled_mvo
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
from datetime import datetime
import os
# os.chdir('C:/Users/신용준/PycharmProjects/pythonProject/webSAA')
#
# index_data = pd.read_excel('resample_input_BY_YJSHIN.xlsx', sheet_name="Daily_price",
#                            names=None, dtype={'Date': datetime}, index_col=0, header=4).dropna()
# # index_data = index_data[index_data.index >= '2012-10-16']
# Resampled_EF = resampled_mvo.simulation(index_data)


number1 = st.number_input('Efficient Frontier Points')
st.write(number1)

number2 = st.number_input('Number of Simulations')
st.write(number2)

number3 = st.number_input('Select Target Return(%)')
st.write(number3)
