from fastapi import FastAPI
from collections import defaultdict
import uvicorn
import psutil

from tora_api.src.trade import Trader, Quoter
from tora_api.src.strategies.strategy import Strategy
from tora_api.src.event.bus import EventBus
from tora_api.src.event.event import EventType
from tora_api.src.event.engine import EventEngine
from tora_api.src.models.request import SubscribeRequest
from tora_api.src.models.fastapi.user import *
from tora_api.src.models.fastapi.error import *
from tora_api.src.tora_stock.traderapi import (CTORATstpInputOrderActionField, TORA_TSTP_EXD_SSE, TORA_TSTP_EXD_SZSE)
from time import sleep
from tora_api.config.config import *
from tora_api.src.log_handler.default_handler import DefaultLogHandler

app = FastAPI()


@app.post('/')
def index():
    print("Hello")


@app.post('/add_strategy')
def add_strategy(user_input: UserStrategyModel):
    req = SubscribeRequest(
        SecurityID=user_input.SecurityID,
        ExchangeID=EXCHANGE_MAPPING_ST2TORA[user_input.ExchangeID]
    )
    print(user_input.SecurityID)
    strategy = Strategy(trader=trader, quoter=quoter, bus=bus, limit_volume=user_input.LimitVolume,
                        cancel_volume=user_input.CancelVolume, position=user_input.Position, count=user_input.Count,
                        log=log, id=user_input.ID)
    if e.load_strategy(strategy):
        strategy.subscribe(req)


@app.post('/remove_strategy')
def remove_strategy(user_input: UserStrategyModel):
    try:
        strategy = e.strategy_dict[user_input.ID]

        strategy.unsubscribe()
        e.remove_strategy(user_input.ID)
    except KeyError:
        error = Error(ErrorID=0, ErrorMsg=f"策略{user_input.ID}不存在")
        return error.model_dump_json()


@app.get('/check_running_strategy')
def check_strategy():
    strategy_group = UserStrategyGroupModel()
    if not e.strategy_dict:
        return Error(ErrorID=0, ErrorMsg=f"服务器中无策略运行")
    else:
        for key in e.strategy_dict.keys():
            strategy = UserStrategyModel()
            strategy.ID = key
            strategy.SecurityID = e.strategy_dict[key].subscribe_request.SecurityID
            strategy.ExchangeID = EXCHANGE_MAPPING_TORA2ST[e.strategy_dict[key].subscribe_request.ExchangeID]
            strategy.LimitVolume = e.strategy_dict[key].buy_trigger_volume
            strategy.CancelVolume = e.strategy_dict[key].cancel_trigger_volume
            strategy.Position = e.strategy_dict[key].position
            strategy.Count = e.strategy_dict[key].trigger_times
            strategy.ID = e.strategy_dict[key].id
            strategy_group.StrategyGroup.append(strategy)
        return strategy_group.model_dump_json()


if __name__ == "__main__":
    p = psutil.Process()
    p.cpu_affinity([0])

    EXCHANGE_MAPPING_ST2TORA = {
        "SSE": TORA_TSTP_EXD_SSE,
        "SZSE": TORA_TSTP_EXD_SZSE
    }

    EXCHANGE_MAPPING_TORA2ST = {
        TORA_TSTP_EXD_SSE: "上交所",
        TORA_TSTP_EXD_SZSE: "深交所"
    }

    log = DefaultLogHandler(name="主引擎", log_type='stdout')
    log.info(f'主程序线程句柄：{p}')
    log.info(f"主程序绑定CPU：{p.cpu_affinity()}")
    bus = EventBus()
    quoter = Quoter(bus, log)
    sleep(1)
    trader = Trader(bus, log)
    quoter.connect(UserID, Password, FrontAddress['level1_xmd_24A'], ACCOUNT_USERID, ADDRESS_FRONT)
    trader.connect(UserID, Password, FrontAddress['level1_trade_24A'], ACCOUNT_USERID, ADDRESS_FRONT)

    e = EventEngine(bus, log)
    e.run()
    uvicorn.run(app)
    log.info("关闭API服务")
    cli = input('输入【1】+回车退出主引擎：')
    if int(cli) == 1:
        e.stop()
        quoter.logout()
        trader.logout()
        quoter.release()
        trader.release()






