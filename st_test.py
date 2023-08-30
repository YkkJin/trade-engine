import os
from datetime import datetime
from pathlib import Path
import pickle

import streamlit as st # web development
import numpy as np # np mean, np random 
import time # to simulate a real time data, time loop 
import plotly.express as px # interactive charts 
import streamlit_authenticator as stauth

RUN_First_Time = True

initialized_state_file_name  = f"init_state_{datetime.now().year}{datetime.now().month}{datetime.now().day}.txt"
if os.path.isfile(initialized_state_file_name):
    print('not first run')
    RUN_First_Time = False
else:
    print('not first run')
    with open(initialized_state_file_name,'a') as f:
        f.write(f'Module ran at {datetime.now()} \n')

st.set_page_config(
    page_title = 'Linkdge-Capital Trader',
    page_icon = '✅',
    layout = 'wide'
)





# dashboard title

st.title("Live Linkdge-Capital Trader Dashboard")
#### Auth

        # ---- SIDEBAR ----

st.sidebar.header("Enter parameters here:")


with st.sidebar:
    number1 = st.number_input('Insert a number',key='a')
    st.write('The current number is ', number1)

    number3 = st.number_input('Insert a number',key='b')
    st.write('The current number is ', number3)

    number2 = st.number_input('Insert a number',key='c')
    st.write('The current number is ', number2)

def test_func(x,y,z):
    print(x,y,z)
    st.write('The current number is ',x,y,z)

st.button("Subscribe", type="primary",on_click = test_func,args=(number1,number2,number3))

if RUN_First_Time :
    print('only run once when app start')
  
    
else:
    st.write(f'RUN_First_Time is {RUN_First_Time}')
    with open(initialized_state_file_name,'a') as f:
        f.write(f'refreshed \n')    
st.write(st.session_state)
#if st.session_state['initialized'] == 'True':

if 'initialized' not in st.session_state:
    st.session_state['initialized'] = 'True'
st.write(st.session_state)
# if 'initialized' not in st.session_state:
#     st.session_state['initialized'] = 'True'
#     print('rerun')
# else:
#     st.write(st.session_state['initialized'])