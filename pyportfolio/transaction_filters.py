from typing import Callable
from casparser.enums import TransactionType

from .models import Transaction
from .utils import or_filter

TransactionFilterType = Callable[[Transaction], bool]


def get_transaction_type_filter(transaction_type: TransactionType) -> TransactionFilterType:
    def transaction_type_filter(transaction: Transaction):
        return transaction.type == transaction_type

    return transaction_type_filter


def get_transaction_older_than_filter(days: int) -> TransactionFilterType:
    def transaction_older_than_filter(transaction: Transaction):
        return transaction.days > days

    return transaction_older_than_filter


# Filters
purchase_transaction_filter = or_filter(
    [
        get_transaction_type_filter(TransactionType.PURCHASE),
        get_transaction_type_filter(TransactionType.PURCHASE_SIP),
    ]
)
redemption_transaction_filter = get_transaction_type_filter(TransactionType.REDEMPTION)
stampduty_transaction_filter = get_transaction_type_filter(TransactionType.MISC)
