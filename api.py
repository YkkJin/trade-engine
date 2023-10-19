from time import sleep

from fastapi import FastAPI

from tora_api.config.tora import *
from tora_api.src.event.bus import EventBus
from tora_api.src.event.engine import EventEngine
from tora_api.src.log_handler.default_handler import DefaultLogHandler
from tora_api.src.models.fastapi.error import *
from tora_api.src.models.fastapi.user import *
from tora_api.src.models.request import SubscribeRequest
from tora_api.src.strategies.fengban_strategy import DaBanStrategy
from tora_api.src.tora_stock.traderapi import (TORA_TSTP_EXD_SSE, TORA_TSTP_EXD_SZSE)
from tora_api.src.trade import Trader, Quoter, L2Quoter

# import psutil

app = FastAPI()


@app.on_event('startup')
def startup_event():
    EXCHANGE_MAPPING_ST2TORA = {
        "SSE": TORA_TSTP_EXD_SSE,
        "SZSE": TORA_TSTP_EXD_SZSE
    }

    EXCHANGE_MAPPING_TORA2ST = {
        TORA_TSTP_EXD_SSE: "上交所",
        TORA_TSTP_EXD_SZSE: "深交所"
    }

    log = DefaultLogHandler(name="主引擎", log_type='stdout')
    # log.info(f'主程序线程句柄：{p}')
    # log.info(f"主程序绑定CPU：{p.cpu_affinity()}")
    bus = EventBus()
    quoter = Quoter(bus, log)
    sleep(1)
    l2quoter = L2Quoter(bus, log)
    sleep(1)
    trader = Trader(bus, log)
    # quoter.connect(UserID, Password, FrontAddress['level1_xmd_24A'], ACCOUNT_USERID, ADDRESS_FRONT)
    # sleep(1)
    l2quoter.connect(UserID, Password, FrontAddress['level2_xmd_SH_test'], ACCOUNT_USERID, ADDRESS_FRONT)
    sleep(1)
    trader.connect(UserID, Password, FrontAddress['level1_trade_24A'], ACCOUNT_USERID, ADDRESS_FRONT)

    e = EventEngine(bus, log)
    e.run()

    app.package = {
        "EXCHANGE_MAPPING_ST2TORA": EXCHANGE_MAPPING_ST2TORA,
        "EXCHANGE_MAPPING_TORA2ST": EXCHANGE_MAPPING_TORA2ST,
        "logger": log,
        "EventBus": bus,
        "Quoter": quoter,
        "L2Quoter": l2quoter,
        "Trader": trader,
        "EventEngine": e
    }


@app.on_event('shutdown')
def shutdown_event():
    app.package["logger"].info("关闭API服务")
    app.package["EventEngine"].stop()
    # app.package["Quoter"].logout()
    app.package["Trader"].logout()
    app.package["L2Quoter"].logout()
    # app.package["Quoter"].release()
    app.package["Trader"].release()
    app.package["L2Quoter"].release()


@app.post('/')
def index():
    print("Hello")


@app.post('/add_strategy')
def add_strategy(user_input: UserStrategyModel):
    req = SubscribeRequest(
        SecurityID=user_input.SecurityID,
        ExchangeID=app.package["EXCHANGE_MAPPING_ST2TORA"][user_input.ExchangeID],
    )

    strategy = DaBanStrategy(trader=app.package["Trader"],
                        quoter=app.package["L2Quoter"],
                        bus=app.package["EventBus"],
                        limit_volume=user_input.LimitVolume * 10000,
                        cancel_volume=user_input.CancelVolume * 10000,
                        count=user_input.Count,
                        position=user_input.Position * 10000,
                        id=user_input.ID,
                        log=app.package["logger"])

    if app.package["EventEngine"].load_strategy(strategy):
        strategy.subscribe(req)


@app.post('/remove_strategy')
def remove_strategy(user_input: UserStrategyModel):
    try:
        strategy = app.package["EventEngine"].strategy_dict[user_input.ID]

        strategy.unsubscribe()
        app.package["EventEngine"].remove_strategy(user_input.ID)
    except KeyError:
        error = Error(ErrorID=0, ErrorMsg=f"策略{user_input.ID}不存在")
        return error


@app.get('/check_running_strategy')
def check_strategy():
    strategy_group = UserStrategyGroupModel()
    if not app.package["EventEngine"].strategy_dict:
        return Error(ErrorID=0, ErrorMsg=f"服务器中无策略运行")
    for key in app.package["EventEngine"].strategy_dict.keys():
        strategy = UserStrategyModel()
        strategy.ID = key
        strategy.SecurityID = app.package["EventEngine"].strategy_dict[key].subscribe_request.SecurityID
        strategy.ExchangeID = app.package["EXCHANGE_MAPPING_TORA2ST"][
            app.package["EventEngine"].strategy_dict[key].subscribe_request.ExchangeID]
        strategy.LimitVolume = app.package["EventEngine"].strategy_dict[key].buy_trigger_volume
        strategy.CancelVolume = app.package["EventEngine"].strategy_dict[key].cancel_trigger_volume
        strategy.Position = app.package["EventEngine"].strategy_dict[key].position
        strategy.Count = app.package["EventEngine"].strategy_dict[key].trigger_times
        strategy.ID = app.package["EventEngine"].strategy_dict[key].id
        strategy_group.StrategyGroup.append(strategy)
    return strategy_group
