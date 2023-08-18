import click
from tora_api.src.trade import Trader
from tora_api.config.config import (
    ACCOUNT_USERID,ADDRESS_FRONT,FrontAddress
)
from tora_api.src.tora_stock.traderapi import (
    TORA_TSTP_D_Buy,
    TORA_TSTP_D_Sell,
    TORA_TSTP_EXD_SSE,
    TORA_TSTP_EXD_SZSE,
    TORA_TSTP_EXD_HK,
    TORA_TSTP_EXD_BSE,
    TORA_TSTP_OST_Cached,
    TORA_TSTP_OPT_LimitPrice,
    TORA_TSTP_OPT_FiveLevelPrice,
    TORA_TSTP_OPT_HomeBestPrice,
    TORA_TSTP_OPT_BestPrice,
    TORA_TSTP_OST_AllTraded,
    TORA_TSTP_OST_AllCanceled,
    TORA_TSTP_OST_Accepted,
    TORA_TSTP_OST_PartTradeCanceled,
    TORA_TSTP_OST_PartTraded,
    TORA_TSTP_OST_Rejected,
    TORA_TERT_RESTART,
    TORA_TERT_QUICK,
    TORA_TSTP_LACT_UserID,
    TORA_TSTP_LACT_AccountID,
    TORA_TSTP_PID_SHBond,
    TORA_TSTP_PID_SHFund,
    TORA_TSTP_PID_SHStock,
    TORA_TSTP_PID_SZBond,
    TORA_TSTP_PID_SZFund,
    TORA_TSTP_PID_SZStock,
    TORA_TSTP_PID_BJStock,
    TORA_TSTP_TC_GFD,
    TORA_TSTP_TC_IOC,
    TORA_TSTP_VC_AV,
    TORA_TSTP_AF_Delete,
    CTORATstpInputOrderField,
    CTORATstpOrderField,
)

@click.command()
def interactive_program():
    while True:
        user_input = click.prompt('Please enter something (or "quit" to exit)')
        user_input_something_else = click.prompt('Please enter something else')
        if user_input.lower() == 'quit':
            break
        else:
            click.echo('You entered: ' + user_input)
@click.command()
def cli():
    user_id = click.prompt('请输入交易ID:')
    password = click.prompt("请输入用户密码:")

    trader = Trader()
    trader.connect(user_id,password,FrontAddress['level1_trade_24A'],ACCOUNT_USERID,ADDRESS_FRONT)

    while True:
        func = click.prompt("""
        请输入希望执行的功能（输入数字或输入quit退出）：
        1. 持仓查询
        2. 交易下单
        
        """)
        if func == "1":
            trader.query_positions()
        elif func == "2":
            SecurityID = click.prompt("""
            输入证券代码:
            """)
            Direction = click.prompt("""
            买卖方向:
            """)
            VolumeTotalOriginal = click.prompt("""
            买卖数量(股):
            """)
            OrderType = click.prompt("""
            委托类型:
            (可选限价)
            """)
            LimitPrice = click.prompt("""
            价格：
            """)
            req = CTORATstpInputOrderField()
            req.SecurityID = SecurityID
            req.ExchangeID = TORA_TSTP_EXD_SSE
            req.ShareholderID = "A00032129"
            req.Direction = TORA_TSTP_D_Sell
            req.VolumeTotalOriginal = int(VolumeTotalOriginal)
            req.LimitPrice = float(LimitPrice)
            req.OrderPriceType = TORA_TSTP_OPT_LimitPrice
            req.TimeCondition = TORA_TSTP_TC_GFD
            req.VolumeCondition = TORA_TSTP_VC_AV 
            trader.send_order(req)
        elif func == "quit":
            trader.logout()
            trader.release()
            break





if __name__ == '__main__':
    cli()
    o