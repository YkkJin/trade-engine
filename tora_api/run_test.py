from src.trade import Trader 
from tora_stock.traderapi import CTORATstpInputOrderActionField
from time import sleep
from config.config import *
from test.test_order import (        
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
order_reqs_sell = [LimitPriceOrderReqSell,]

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
    trader = Trader()
    trader.connect(UserID,Password,FrontAddress['level1_trade_24A'],ACCOUNT_USERID,ADDRESS_FRONT)
    sleep(1)
    trader.query_accounts()
    sleep(1)
    trader.query_orders()
    sleep(1)
    trader.query_positions()
    sleep(1)

   # test_sell_order(trader)

    sleep(5)
    trader.query_orders()
    trader.query_orders()
    input() 

    trader.logout()
    trader.release()

    
        
