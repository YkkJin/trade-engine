from pydantic import BaseModel


class Error(BaseModel):
    ErrorID: int = 0
    ErrorMsg: str = ""