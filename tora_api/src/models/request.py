from pydantic import BaseModel

from ..tora_stock.traderapi import (
    TORA_TSTP_D_Buy,
    TORA_TSTP_D_Sell,
    TORA_TSTP_OPT_LimitPrice,
    TORA_TSTP_TC_GFD,
    TORA_TSTP_VC_AV,
    TORA_TSTP_AF_Delete
)


class CancelRequest(BaseModel):
    ExchangeID: str = ""
    SecurityID: str = ""
    OrderRef: int = 0
    FrontID: int = 0
    SessionID: int = 0
    ActionFlag: int = TORA_TSTP_AF_Delete
    OrderActionRef: int = 0

from tora_api.src.tora_stock.traderapi import  TORA_TSTP_EXD_SSE
class SubscribeRequest(BaseModel):
    ExchangeID: str = ""
    SecurityID: str = ""


class OrderRequest(BaseModel):
    ShareholderID: str = ""
    OrderRef: str = ""
    ExchangeID: str = ""
    SecurityID: str = ""
    Direction: str = ""
    VolumeTotalOriginal: int = 0
    LimitPrice: float = 0.0
    OrderPriceType: str = ""
    TimeCondition: str = ""
    VolumeCondition: str = ""
    OrderID: str = ""

    def create_cancel_order_request(self, order_action_ref: int) -> CancelRequest:
        '''
        Params:
        order_action_ref: 委托撤单编号
        '''
        cancel_req: CancelRequest = CancelRequest()
        cancel_req.ExchangeID = self.ExchangeID
        cancel_req.SecurityID = self.SecurityID
        front_id, session_id, order_ref = self.OrderID.split("_")
        cancel_req.FrontID = int(front_id)
        cancel_req.SessionID = int(session_id)
        cancel_req.OrderRef = int(order_ref)
        cancel_req.OrderActionRef = order_action_ref

        return cancel_req


class LimitPriceBuyRequest(OrderRequest):
    Direction: int = TORA_TSTP_D_Buy
    OrderPriceType: int = TORA_TSTP_OPT_LimitPrice
    TimeCondition: int = TORA_TSTP_TC_GFD
    VolumeCondition: int = TORA_TSTP_VC_AV


class LimitPriceSellRequest(OrderRequest):
    Direction: int = TORA_TSTP_D_Sell
    OrderPriceType: int = TORA_TSTP_OPT_LimitPrice
    TimeCondition: int = TORA_TSTP_TC_GFD
    VolumeCondition: int = TORA_TSTP_VC_AV
