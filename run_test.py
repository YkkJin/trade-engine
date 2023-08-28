from tora_api.src.trade import Trader, Quoter
from tora_api.src.strategies.strategy import Strategy
from tora_api.src.event.bus import EventBus
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


if __name__ == "__main__":
    bus = EventBus()
    quoter = Quoter(bus)
    sleep(1)
    trader = Trader(bus)
    quoter.connect(UserID, Password, FrontAddress['level1_xmd'], ACCOUNT_USERID, ADDRESS_FRONT)
    trader.connect(UserID,Password,FrontAddress['level1_trade'],ACCOUNT_USERID, ADDRESS_FRONT)
    sleep(1)
    req = SubscribeRequest(
        SecurityID='601099',
        ExchangeID=TORA_TSTP_EXD_SSE
    )

    strategy = Strategy(trader=trader, quoter=quoter, limit_volume=10000000, cancel_volume=80000000, position=10000)
    strategy.subscribe(req)

    e = EventEngine(bus, strategy=strategy)
    e.run()
