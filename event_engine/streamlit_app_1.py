import os
from datetime import datetime
from pathlib import Path
import pickle

import streamlit as st # web development
import numpy as np # np mean, np random 
import time # to simulate a real time data, time loop 
import plotly.express as px # interactive charts 
import streamlit_authenticator as stauth


st.set_page_config(
    page_title = 'Linkdge-Capital Trader',
    page_icon = '✅',
    layout = 'wide'
)

# dashboard title

st.title("Live Linkdge-Capital Trader Dashboard")
#### Auth

names = ["chou xiang luo", "cosmo"]
usernames = ["chouxiangluo", "rmiller"]
# load hashed passwords
file_path = Path(__file__).parent / "hashed_pw.pkl"
with file_path.open("rb") as file:
    hashed_passwords = pickle.load(file)

credentials = {
    "usernames":{
        usernames[0]:{
            "name":names[0],
            "password":hashed_passwords[0]
            },
        usernames[1]:{
            "name":names[1],
            "password":hashed_passwords[1]
            }            
        }
    }
# authenticator = stauth.Authenticate(names, usernames, hashed_passwords,
#     "sales_dashboard", "abcdef", cookie_expiry_days=30)
authenticator = stauth.Authenticate(credentials, "app_home", "auth", cookie_expiry_days=0)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/password is incorrect")

if authentication_status == None:
    st.warning("Please enter your username and password")

if authentication_status:

    # creating a single-element container.
    placeholder = st.empty()

    # dataframe filter 


    # near real-time / live feed simulation 

    close_list = []
    while True: 
        
        with open(f"test_{datetime.now().year}_{datetime.now().month}_{datetime.now().day}.csv", 'rb') as f:

            try:  # catch OSError in case of a one line file 
                f.seek(-2, os.SEEK_END)
                while f.read(1) != b'\n':
                    f.seek(-2, os.SEEK_CUR)
            except OSError:
                f.seek(0)
            last_line = f.readline().decode()
            print(last_line.split(','))
            close = float(last_line.split(',')[1])
            close_list.append(close)

        with placeholder.container():
            # create three columns
            kpi1 ,kpi2= st.columns(2)

            # fill in those three columns with respective metrics or KPIs 
            kpi1.metric(label="Stock PRICE ⏳", value=round(close), delta= round(close) )


            # create two columns for charts 

            fig_col1 ,fig_col2= st.columns(2)
            with fig_col1:
                st.markdown("### First Chart")
                fig = px.line(close_list)
                st.write(fig)

            st.markdown("### Detailed Data View")
            #st.dataframe(df)
            time.sleep(1)
        #placeholder.empty()
