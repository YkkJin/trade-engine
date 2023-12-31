import sys
sys.path.append('../../')
from tora_api.src.trade import Trader, Quoter
from tora_api.src.strategies.strategy import Strategy
from tora_api.src.event.bus import EventBus
from tora_api.src.event.engine import EventEngine
from tora_api.src.models.request import SubscribeRequest
from tora_api.src.tora_stock.traderapi import (CTORATstpInputOrderActionField, TORA_TSTP_EXD_SSE)
from time import sleep
from tora_api.config.tora import *
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


if __name__ == "__main__":
    log = DefaultLogHandler(name="主引擎", log_type='stdout',filepath='main_engine.log')
    bus = EventBus()
    quoter = Quoter(bus,log)
    sleep(1)
    trader = Trader(bus,log)
    quoter.connect(UserID, Password, FrontAddress['level1_xmd_24A'], ACCOUNT_USERID, ADDRESS_FRONT)
    trader.connect(UserID, Password, FrontAddress['level1_trade_24A'], ACCOUNT_USERID, ADDRESS_FRONT)
    sleep(1)
    req = SubscribeRequest(
        SecurityID='600114',
        ExchangeID=TORA_TSTP_EXD_SSE
    )

    strategy = Strategy(bus=bus, trader=trader, quoter=quoter, limit_volume=10000000, cancel_volume=800000000000, position=10000,count = 3,log = log,id=1)

    strategy.subscribe(req)

    e = EventEngine(bus, log = log)
    e.run()
    cli = input('输入【1】+回车退出主引擎：\n')
    if int(cli) == 1:
        e.stop()
        quoter.logout()
        trader.logout()
        quoter.release()
        trader.release()


