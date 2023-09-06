from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn


from tora_api.src.trade import Trader, Quoter
from tora_api.src.strategies.strategy import Strategy
from tora_api.src.event.bus import EventBus
from tora_api.src.event.event import EventType
from tora_api.src.event.engine import EventEngine
from tora_api.src.models.request import SubscribeRequest
from tora_api.src.tora_stock.traderapi import (CTORATstpInputOrderActionField, TORA_TSTP_EXD_SSE)
from time import sleep
from tora_api.config.config import *
from tora_api.src.log_handler.default_handler import DefaultLogHandler
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

app = FastAPI()
class User_Input(BaseModel):
    Name: str
    SecurityID:int
    limit_volume:int
    cancel_volume:int
    position:int
    count:int

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

@app.post('/add_strategy')
def add_strategy(input:User_Input):
    req = SubscribeRequest(
        SecurityID=str(input.SecurityID),
        ExchangeID=TORA_TSTP_EXD_SSE
    )
    if input.Name in e.strategy_dict.keys():
        return f"strategy {input.Name}, already exist, please choose another name"
    else:
        strategy = Strategy(trader=trader, quoter=quoter,bus=bus, limit_volume=input.limit_volume, cancel_volume=input.cancel_volume, position=input.position,count=input.count)
        e.strategy_dict[input.Name] = strategy
        strategy.subscribe(req) 
        bus.register(EventType.TICK, strategy.on_tick)
        bus.register(EventType.TRADE, strategy.on_trade)
        bus.register(EventType.ORDER, strategy.on_order)
        return f"added strategy {input.Name},{input.SecurityID} , {input.limit_volume}, {input.cancel_volume}, {input.position}"

@app.post('/remove_strategy')
def remove_strategy2(input:User_Input):
    req = SubscribeRequest(
        SecurityID=str(input.SecurityID),
        ExchangeID=TORA_TSTP_EXD_SSE
    )
    print(f"type of name is {type(input.Name)}")
    print(f"curr strategy is {e.strategy_dict.keys()}")
    print(f"s name is {input.Name}, it is in current strategies {input.Name in e.strategy_dict.keys()}")
    if input.Name in e.strategy_dict.keys():
        print(f'trying to remove {input.Name}')
        strategy = e.strategy_dict[input.Name] 
        strategy.unsubscribe(req) 

        bus.unregister(EventType.TICK, strategy.on_tick)
        bus.unregister(EventType.TRADE, strategy.on_trade)
        bus.unregister(EventType.ORDER, strategy.on_order)
        e.strategy_dict.pop(input.Name) 
        print(f"curr strate gy is {e.strategy_dict.keys()}")
        return f"removed strategy {input.Name}  , {input.SecurityID} "
        
    else:
        return f"{input.Name} not found, Curr strategies are {e.strategy_dict.keys()}"
    
@app.get('/check_curr_strategy')
def check_curr_strategy():
    return f"Curr strategies are {e.strategy_dict.keys()}"

if __name__ == "__main__":
    log = DefaultLogHandler(name="主引擎", log_type='stdout',filepath='main_engine.log')
    bus = EventBus()
    quoter = Quoter(bus,log)
    sleep(1)
    trader = Trader(bus,log)
    quoter.connect(UserID, Password, FrontAddress['level1_xmd_24A'], ACCOUNT_USERID, ADDRESS_FRONT)
    trader.connect(UserID,Password,FrontAddress['level1_trade_24A'],ACCOUNT_USERID, ADDRESS_FRONT)
    sleep(1)


    e = EventEngine(bus,log)
    e.run()
    uvicorn.run(app,  port=8000)