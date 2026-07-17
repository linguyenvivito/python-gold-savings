from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

class TransactionResponse(BaseModel):
    id: str
    account_id: str
    gold_product_id: str
    store_id: str
    transaction_type: str
    quantity: Decimal
    executed_price: Decimal
    cash_amount: Decimal
    fee: Decimal
    note: str
    created_at: datetime

