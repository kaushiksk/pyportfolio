import datetime
from decimal import Decimal
from typing import List, Optional, Union
from casparser.types import TransactionDataType
from pydantic import BaseModel
from pydantic.annotated_types import create_model_from_typeddict

TransactionBase = create_model_from_typeddict(TransactionDataType)


class Transaction(TransactionBase):
    date: datetime.datetime
    days: int
    balance: Union[Decimal, None]


class Scheme(BaseModel):
    name: str
    amfi: str
    units: Decimal
    nav: Decimal
    type: Union[str, None]
    subtype: Union[str, None]
    valuation: Optional[Decimal]
    transactions: Optional[List[Transaction]]

    def __init__(self, **data):
        super().__init__(**data)
        self.valuation = self.units * self.nav
