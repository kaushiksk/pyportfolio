from copy import deepcopy
from decimal import Decimal
from typing import List
from .models import Transaction
from .transaction_filters import (
    TransactionFilterType,
    redemption_transaction_filter,
    purchase_transaction_filter,
)


def get_filtered_transactions(
    filter_to_apply: TransactionFilterType, transactions: List[Transaction]
):
    """Apply filter on transactions and return the filtered list"""
    return list(filter(filter_to_apply, transactions))


def get_purchase_transactions_for_active_units(transactions: List[Transaction]):
    """Returns all purchase transactions for units that haven't been redeemed yet

    Args:
        transactions (Transaction): list of transactions to check in

    Returns:
        List[Transaction]: All purchase transactions for units that haven't been redeemed
    """
    redeemed_transactions = get_filtered_transactions(redemption_transaction_filter, transactions)

    if len(redeemed_transactions) > 0:
        total_redeemed_units = abs(
            sum([transaction.units for transaction in redeemed_transactions])
        )
    else:
        total_redeemed_units = Decimal("0.0")

    # Perform deepcopy to avoid modifying the source reference
    purchase_transactions: List[Transaction] = deepcopy(
        get_filtered_transactions(purchase_transaction_filter, transactions)
    )

    if total_redeemed_units == 0:
        return purchase_transactions

    computed_units = Decimal("0.0")

    # We keep deleting transactions from top until all redemptions are satisfied
    while len(purchase_transactions) > 0:
        computed_units += purchase_transactions[0].units

        if computed_units <= total_redeemed_units:
            # All these units were extinguished during redemption
            purchase_transactions.pop(0)
        else:
            # Part of the units were extinguished
            purchase_transactions[0].units = computed_units - total_redeemed_units
            purchase_transactions[0].amount = (
                purchase_transactions[0].units * purchase_transactions[0].nav
            )
            break  # No more units were extinguished

    return purchase_transactions
