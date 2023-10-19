import streamlit as st  # web development
import json
from pydantic import BaseModel
from tora_api.src.models.fastapi.user import (UserStrategyModel, UserStrategyGroupModel)
from tora_api.src.models.fastapi.error import Error
import pandas as pd

import json
import requests

# Init Session state

if "strategy_id" not in st.session_state:
    st.session_state.strategy_id = 0
if "running_strategy" not in st.session_state:
    st.session_state.running_strategy = ''
if "strategy_container" not in st.session_state:
    st.session_state.strategy_container = False

st.set_page_config(
    page_title='领桥量化',
    page_icon='✅',
    layout='wide'
)

# dashboard title

st.title("程序化盘中跟板策略客户端v0.0.1")
#### Auth

# ---- SIDEBAR ----

st.sidebar.header("策略编辑")


def add_strategy(user_input: UserStrategyModel):
    user_input.ID = st.session_state.strategy_id
    res = requests.post(url="http://127.0.0.1:8000/add_strategy", data=user_input.model_dump_json())
    if res.status_code == 200:
        check_strategy()
    else:
        st.error('策略提交异常', icon='🚨')


def remove_strategy(user_input: UserStrategyModel):
    res = requests.post(url="http://127.0.0.1:8000/remove_strategy", data=user_input.model_dump_json())
    if res.status_code == 200:
        st.success('策略删除成功!', icon='✅')
        check_strategy()
        st.session_state.strategy_id -= 1
        if st.session_state.running_strategy == None:
            st.session_state.strategy_container = False
            st.session_state.strategy_id = 0

    else:
        st.error('策略删除异常', icon='🚨')


def check_strategy():
    res = requests.get(url="http://127.0.0.1:8000/check_running_strategy")
    if 'ErrorMsg' in res.json().keys():
        st.session_state.strategy_container = False
    else:
        st.session_state.running_strategy = res.json()
    st.success('策略查询成功', icon='✅')


with st.sidebar:
    submit_container = st.container()
    submit_container.subheader('策略提交')
    stock_code = submit_container.text_input('输入股票代码(6位数字)：',value = '600000')
    exchange = submit_container.selectbox('选择交易所：', ('SSE', 'SZSE'))
    limit_volume = submit_container.number_input('封单金额(万)：', min_value=100, step=100)
    cancel_volume = submit_container.number_input('撤单金额(万)：', min_value=100, step=100)
    position = submit_container.number_input('打板金额(万)：', min_value=1, step=100)
    count = submit_container.number_input('撤单次数：', min_value=1, step=1)

    user_strategy = UserStrategyModel()

    user_strategy.SecurityID = stock_code
    user_strategy.ExchangeID = exchange
    user_strategy.LimitVolume = int(limit_volume)
    user_strategy.CancelVolume = int(cancel_volume)
    user_strategy.Position = int(position)
    user_strategy.Count = int(count)
    submit = submit_container.button("提交策略", type="primary", on_click=add_strategy, args=(user_strategy,),
                                     use_container_width=True)
    check = submit_container.button("查询策略", type="secondary", on_click=check_strategy, use_container_width=True)

    delete_container = st.container()
    delete_container.subheader('策略删除')
    strategy_id = delete_container.number_input('输入策略编号', min_value=0, step=1)
    user_remove_strategy = UserStrategyModel()
    user_remove_strategy.ID = strategy_id
    remove = delete_container.button("删除策略", type="secondary", on_click=remove_strategy,
                                     args=(user_remove_strategy,),
                                     use_container_width=True)
    if submit:
        st.session_state.strategy_id += 1
        st.session_state.strategy_container = True


# ---- container ----
container = st.container()
container.header('策略管理')

if st.session_state.strategy_container:
    df = pd.DataFrame.from_dict(data=st.session_state.running_strategy['StrategyGroup'])
    container.dataframe(
        df,
        column_config={
            'SecurtiyID': '证券代码',
            'ExchangeID': '交易所',
            'LimitVolume': '封单额',
            'CancelVolume': '撤单额',
            'Position': '仓位',
            'Count': '撤单次数',
            'ID': '策略编号'
        },
        column_order=('ID', 'SecurityID', 'ExchangeID', 'LimitVolume', 'CancelVolume', 'Position', 'Count'),
        hide_index=True,
        use_container_width=True
    )

else:
    st.write(":u7121: 无策略运行")


