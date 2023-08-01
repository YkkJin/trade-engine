from tora_stock.traderapi import (
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

'''
买入指令测试

'''

'''
***** 限价
'''
LimitPriceOrderReq = CTORATstpInputOrderField()
LimitPriceOrderReq.SecurityID = '600000'
LimitPriceOrderReq.ExchangeID  = TORA_TSTP_EXD_SSE
LimitPriceOrderReq.ShareholderID = "A00032129"
LimitPriceOrderReq.Direction = TORA_TSTP_D_Buy
LimitPriceOrderReq.VolumeTotalOriginal = 200
LimitPriceOrderReq.LimitPrice = 7.60 
LimitPriceOrderReq.OrderPriceType = TORA_TSTP_OPT_LimitPrice
LimitPriceOrderReq.TimeCondition = TORA_TSTP_TC_GFD
LimitPriceOrderReq.VolumeCondition = TORA_TSTP_VC_AV

'''
***** 最优五档成交剩余转撤销
'''
FiveLevelPriceToCancelOrderReq = CTORATstpInputOrderField()
FiveLevelPriceToCancelOrderReq.SecurityID = '600000'
FiveLevelPriceToCancelOrderReq.ExchangeID  = TORA_TSTP_EXD_SSE
FiveLevelPriceToCancelOrderReq.ShareholderID = "A00032129"
FiveLevelPriceToCancelOrderReq.Direction = TORA_TSTP_D_Buy
FiveLevelPriceToCancelOrderReq.VolumeTotalOriginal = 200
FiveLevelPriceToCancelOrderReq.LimitPrice = 7.60    #报单交易所为上交所时，需申明保护限价
FiveLevelPriceToCancelOrderReq.OrderPriceType = TORA_TSTP_OPT_FiveLevelPrice
FiveLevelPriceToCancelOrderReq.TimeCondition = TORA_TSTP_TC_IOC
FiveLevelPriceToCancelOrderReq.VolumeCondition = TORA_TSTP_VC_AV

'''
***** 最优五档成交剩余转限价
'''
FiveLevelPriceToLimitOrderReq = CTORATstpInputOrderField()
FiveLevelPriceToLimitOrderReq.SecurityID = '600000'
FiveLevelPriceToLimitOrderReq.ExchangeID  = TORA_TSTP_EXD_SSE
FiveLevelPriceToLimitOrderReq.ShareholderID = "A00032129"
FiveLevelPriceToLimitOrderReq.Direction = TORA_TSTP_D_Buy
FiveLevelPriceToLimitOrderReq.VolumeTotalOriginal = 200
FiveLevelPriceToLimitOrderReq.LimitPrice = 7.60
FiveLevelPriceToLimitOrderReq.OrderPriceType = TORA_TSTP_OPT_FiveLevelPrice
FiveLevelPriceToLimitOrderReq.TimeCondition = TORA_TSTP_TC_GFD
FiveLevelPriceToLimitOrderReq.VolumeCondition = TORA_TSTP_VC_AV

'''
***** 本方最优
'''
HomeBestPriceOrderReq = CTORATstpInputOrderField()
HomeBestPriceOrderReq.SecurityID = '600000'
HomeBestPriceOrderReq.ExchangeID  = TORA_TSTP_EXD_SSE
HomeBestPriceOrderReq.ShareholderID = "A00032129"
HomeBestPriceOrderReq.Direction = TORA_TSTP_D_Buy
HomeBestPriceOrderReq.VolumeTotalOriginal = 200
HomeBestPriceOrderReq.LimitPrice = 7.60
HomeBestPriceOrderReq.OrderPriceType = TORA_TSTP_OPT_HomeBestPrice
HomeBestPriceOrderReq.TimeCondition = TORA_TSTP_TC_GFD
HomeBestPriceOrderReq.VolumeCondition = TORA_TSTP_VC_AV

'''
***** 对手方最优
'''
BestPriceOrderReq = CTORATstpInputOrderField()
BestPriceOrderReq.SecurityID = '600000'
BestPriceOrderReq.ExchangeID  = TORA_TSTP_EXD_SSE
BestPriceOrderReq.ShareholderID = "A00032129"
BestPriceOrderReq.Direction = TORA_TSTP_D_Buy
BestPriceOrderReq.VolumeTotalOriginal = 200
BestPriceOrderReq.LimitPrice = 7.60
BestPriceOrderReq.OrderPriceType = TORA_TSTP_OPT_BestPrice
BestPriceOrderReq.TimeCondition = TORA_TSTP_TC_GFD
BestPriceOrderReq.VolumeCondition = TORA_TSTP_VC_AV


'''
卖出指令测试
'''

'''
***** 限价卖出
'''
LimitPriceOrderReqSell = CTORATstpInputOrderField()
LimitPriceOrderReqSell.SecurityID = '600000'
LimitPriceOrderReqSell.ExchangeID  = TORA_TSTP_EXD_SSE
LimitPriceOrderReqSell.ShareholderID = "A00032129"
LimitPriceOrderReqSell.Direction = TORA_TSTP_D_Sell
LimitPriceOrderReqSell.VolumeTotalOriginal = 100
LimitPriceOrderReqSell.LimitPrice = 7.60
LimitPriceOrderReqSell.OrderPriceType = TORA_TSTP_OPT_LimitPrice
LimitPriceOrderReqSell.TimeCondition = TORA_TSTP_TC_GFD
LimitPriceOrderReqSell.VolumeCondition = TORA_TSTP_VC_AV 

'''
***** 最优五档成交剩余转撤销
'''
FiveLevelPriceToCancelOrderReqSell = CTORATstpInputOrderField()
FiveLevelPriceToCancelOrderReqSell.SecurityID = '600000'
FiveLevelPriceToCancelOrderReqSell.ExchangeID  = TORA_TSTP_EXD_SSE
FiveLevelPriceToCancelOrderReqSell.ShareholderID = "A00032129"
FiveLevelPriceToCancelOrderReqSell.Direction = TORA_TSTP_D_Sell
FiveLevelPriceToCancelOrderReqSell.VolumeTotalOriginal = 200
FiveLevelPriceToCancelOrderReqSell.LimitPrice = 7.60 
FiveLevelPriceToCancelOrderReqSell.OrderPriceType = TORA_TSTP_OPT_FiveLevelPrice
FiveLevelPriceToCancelOrderReqSell.TimeCondition = TORA_TSTP_TC_IOC
FiveLevelPriceToCancelOrderReqSell.VolumeCondition = TORA_TSTP_VC_AV

'''
***** 最优五档成交剩余转限价
'''
FiveLevelPriceToLimitOrderReqSell = CTORATstpInputOrderField()
FiveLevelPriceToLimitOrderReqSell.SecurityID = '600000'
FiveLevelPriceToLimitOrderReqSell.ExchangeID  = TORA_TSTP_EXD_SSE
FiveLevelPriceToLimitOrderReqSell.ShareholderID = "A00032129"
FiveLevelPriceToLimitOrderReqSell.Direction = TORA_TSTP_D_Sell
FiveLevelPriceToLimitOrderReqSell.VolumeTotalOriginal = 200
FiveLevelPriceToLimitOrderReqSell.LimitPrice = 7.60
FiveLevelPriceToLimitOrderReqSell.OrderPriceType = TORA_TSTP_OPT_FiveLevelPrice
FiveLevelPriceToLimitOrderReqSell.TimeCondition = TORA_TSTP_TC_GFD
FiveLevelPriceToLimitOrderReqSell.VolumeCondition = TORA_TSTP_VC_AV

'''
***** 本方最优
'''
HomeBestPriceOrderReqSell = CTORATstpInputOrderField()
HomeBestPriceOrderReqSell.SecurityID = '600000'
HomeBestPriceOrderReqSell.ExchangeID  = TORA_TSTP_EXD_SSE
HomeBestPriceOrderReqSell.ShareholderID = "A00032129"
HomeBestPriceOrderReqSell.Direction = TORA_TSTP_D_Sell
HomeBestPriceOrderReqSell.VolumeTotalOriginal = 200
HomeBestPriceOrderReqSell.LimitPrice = 7.60
HomeBestPriceOrderReqSell.OrderPriceType = TORA_TSTP_OPT_HomeBestPrice
HomeBestPriceOrderReqSell.TimeCondition = TORA_TSTP_TC_GFD
HomeBestPriceOrderReqSell.VolumeCondition = TORA_TSTP_VC_AV

'''
***** 对手方最优
'''
BestPriceOrderReqSell = CTORATstpInputOrderField()
BestPriceOrderReqSell.SecurityID = '600000'
BestPriceOrderReqSell.ExchangeID  = TORA_TSTP_EXD_SSE
BestPriceOrderReqSell.ShareholderID = "A00032129"
BestPriceOrderReqSell.Direction = TORA_TSTP_D_Sell
BestPriceOrderReqSell.VolumeTotalOriginal = 200
BestPriceOrderReqSell.LimitPrice = 7.60
BestPriceOrderReqSell.OrderPriceType = TORA_TSTP_OPT_BestPrice
BestPriceOrderReqSell.TimeCondition = TORA_TSTP_TC_GFD
BestPriceOrderReqSell.VolumeCondition = TORA_TSTP_VC_AV


'''
***** 撤单测试 
'''

LimitPriceOrderReqCancel = CTORATstpInputOrderField()
LimitPriceOrderReqCancel.SecurityID = '600000'
LimitPriceOrderReqCancel.ExchangeID  = TORA_TSTP_EXD_SSE
LimitPriceOrderReqCancel.ShareholderID = "A00032129"
LimitPriceOrderReqCancel.Direction = TORA_TSTP_D_Buy
LimitPriceOrderReqCancel.VolumeTotalOriginal = 200
LimitPriceOrderReqCancel.LimitPrice = 7.90
LimitPriceOrderReqCancel.OrderPriceType = TORA_TSTP_OPT_LimitPrice
LimitPriceOrderReqCancel.TimeCondition = TORA_TSTP_TC_GFD
LimitPriceOrderReqCancel.VolumeCondition = TORA_TSTP_VC_AV