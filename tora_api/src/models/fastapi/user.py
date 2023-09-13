from pydantic import BaseModel


class UserStrategyModel(BaseModel):
    SecurityID: str = ""
    ExchangeID: str = ""
    LimitVolume: int = 0
    CancelVolume: int = 0
    Position: int = 0
    Count: int = 0
    ID: int = 0


class UserStrategyGroupModel(BaseModel):
    StrategyGroup: list = []