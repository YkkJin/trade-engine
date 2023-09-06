import streamlit as st # web development
from pydantic import BaseModel
import json
import requests

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

class User_Input(BaseModel):
    Name: str
    SecurityID:int
    limit_volume:int
    cancel_volume:int
    position:int
    count:int

def add_strategy(inputs):

    res = requests.post(url="http://127.0.0.1:8000/add_strategy", data = json.dumps(inputs))
    print(f'res is {res}')
    st.subheader(f'response from API is {res.json()}')
def remove_strategy(inputs):

    res = requests.post(url="http://127.0.0.1:8000/remove_strategy", data = json.dumps(inputs))
    print(f'res is {res}')
    st.subheader(f'response from API is {res.json()}')

def check_strategy():

    res = requests.get(url="http://127.0.0.1:8000/check_curr_strategy")
    print(f'res is {res}')
    st.subheader(f'response from API is {res.json()}')
with st.sidebar:
    name = st.text_input('Insert a strategy name',key='s_name')
    number1 = st.number_input('Insert a stock',key='a')
    number1=int(number1)
    print(type(number1))
    st.write('The current stock is ', number1)
    number2 = st.number_input('Insert a limit_volume',key='b')
    st.write('The current number is ', number2)
    number3 = st.number_input('Insert a cancel_volume',key='c')
    st.write('The current number is ', number3)
    number4 = st.number_input('Insert a position',key='d')
    st.write('The current number is ', number4)
    number5 = int(st.number_input('Insert a count',key='e'))
    st.write('The current number is ', number5)
    #input = User_Input(SecurityID = number1,limit_volume = number2,cancel_volume = number3,position = number4)
    input = {"Name":name,"SecurityID" : number1,"limit_volume" : number2,"cancel_volume" : number3,"position" : number4,"count":number5}
    # input.SecurityID = number1
    # input.limit_volume = number2
    # input.cancel_volume = number3
    # input.position = number4

    st.button("Subscribe", type="primary",on_click = add_strategy ,args= (input,))
    st.button("Unsubscribe", type="primary",on_click = remove_strategy ,args= (input,))
    st.button("Check Strategy", type="primary",on_click = check_strategy)