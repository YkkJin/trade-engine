import os
from datetime import datetime
import streamlit as st # web development

RUN_First_Time = True

initialized_state_file_name  = f"init_state_{datetime.now().year}{datetime.now().month}{datetime.now().day}.txt"
if os.path.isfile(initialized_state_file_name):
    print('not first run')
    RUN_First_Time = False
else:
    print('not first run')
    with open(initialized_state_file_name,'a') as f:
        f.write(f'Module First ran at {datetime.now()} \n')


print('rerun')
from tora_api.src.trade import Trader, Quoter
from tora_api.src.strategies.strategy import Strategy
from tora_api.src.event.bus import EventBus
from tora_api.src.event.type import EventType
from tora_api.src.event.engine import EventEngine
from tora_api.src.models.request import SubscribeRequest
from tora_api.src.tora_stock.traderapi import (CTORATstpInputOrderActionField, TORA_TSTP_EXD_SSE)
from time import sleep
from tora_api.config.config import *
from tora_api.test.test_order import (
    LimitPriceOrderReq,
    LimitPriceOrderReqSell,
    FiveLevelPriceToCancelOrderReq,
    FiveLevelPriceToCancelOrderReqSell,
    FiveLevelPriceToLimitOrderReq,
    FiveLevelPriceToLimitOrderReqSell,
    HomeBestPriceOrderReq,
    HomeBestPriceOrderReqSell,
    BestPriceOrderReq,
    BestPriceOrderReqSell,
    LimitPriceOrderReqCancel
)

order_reqs = [LimitPriceOrderReq,
            FiveLevelPriceToLimitOrderReq,
            FiveLevelPriceToCancelOrderReq,
            HomeBestPriceOrderReq,
            BestPriceOrderReq]
order_reqs_sell = [LimitPriceOrderReqSell,
                LimitPriceOrderReqSell,
                LimitPriceOrderReqSell,
                LimitPriceOrderReqSell]

cancel_order_reqs = [LimitPriceOrderReqCancel]


def test_buy_order(trader: Trader) -> bool:
    for order_req in order_reqs:
        try:
            trader.send_order(order_req)
        except ValueError:
            return False
    return True


def test_sell_order(trader: Trader) -> bool:
    for order_req in order_reqs_sell:
        try:
            trader.send_order(order_req)
        except ValueError:
            return False
    return True


def test_cancel_order(trader: Trader) -> bool:
    for order_req in cancel_order_reqs:
        try:
            order_id = trader.send_order(order_req)
            front_id, session_id, order_ref = order_id.split('_')
            cancel_req = CTORATstpInputOrderActionField()
            cancel_req.ExchangeID = order_req.ExchangeID
            cancel_req.SecurityID = order_req.SecurityID
            cancel_req.OrderRef = int(order_ref)
            cancel_req.FrontID = int(front_id)
            cancel_req.SessionID = int(session_id)
            trader.cancel_order(cancel_req)
        except ValueError:
            return False
    return True

def add_strategy(engine,trader,quoter,code,limit_volume,cancel_volume,position):
    req = SubscribeRequest(
        SecurityID=code,
        ExchangeID=TORA_TSTP_EXD_SSE
    )
    strategy = Strategy(trader=trader, 
                        quoter=quoter, 
                        limit_volume=limit_volume, 
                        cancel_volume=cancel_volume, 
                        position=position)#limit_volume=10000000, cancel_volume=80000000, position=10000
    strategy.subscribe(req)
    print('adding strategy')
    engine.bus.register(EventType.TICK, strategy.on_tick)
    engine.bus.register(EventType.TRADE, strategy.on_trade)
    engine.bus.register(EventType.ORDER, strategy.on_order)

def set_up_page():
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
        number1 = st.text_input('Insert a stock',key='a')
        st.write('The current stock is ', number1)
        number2 = st.number_input('Insert a limit_volume',key='b')
        st.write('The current number is ', number2)
        number3 = st.number_input('Insert a cancel_volume',key='c')
        st.write('The current number is ', number3)
        number4 = st.number_input('Insert a position',key='d')
        st.write('The current number is ', number4)
    return number1,number2,number3,number4

@st.cache_resource
def load_component():
    bus = EventBus()
    quoter = Quoter(bus)
    trader = Trader(bus)
    quoter.connect(UserID, Password, FrontAddress['level1_xmd_24A'], ACCOUNT_USERID, ADDRESS_FRONT)
    trader.connect(UserID,Password,FrontAddress['level1_trade_24A'],ACCOUNT_USERID, ADDRESS_FRONT)
    e = EventEngine(bus)
    e.run()
    print('component loaded')
    return e,bus,quoter,trader 
    
if __name__ == "__main__":
    number1,number2,number3,number4 = set_up_page()

    
    e,bus,quoter,trader = load_component()
    print(f"id of event engine is {id(e.bus)}")
    if RUN_First_Time :
        print('only run once when app start')



        
    with st.sidebar:
        st.button("Subscribe", type="primary",on_click = add_strategy ,args=(e,trader,quoter,number1,number2,number3,number4))



