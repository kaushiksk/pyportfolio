from decimal import Decimal
from typing import List

from .constants import ELSS, EQUITY
from .models import Scheme
from .transaction_utils import get_purchase_transactions_for_active_units, get_filtered_transactions
from .transaction_filters import get_transaction_older_than_filter
from .scheme_filters import SchemeFilterType
from .utils import logger


def get_filtered_schemes(filter_to_apply: SchemeFilterType, schemes: List[Scheme]):
    """Apply filter on schemes and return the filtered list"""
    return list(filter(filter_to_apply, schemes))


def analyze_ltcg_tax_harvesting(scheme: Scheme):
    """Analyze Long Term Capital Gains opportunities

    Args:
        scheme (Scheme):

    Returns:
        dict: ltgc stats for given scheme
    """
    logger.debug(f"LTCG Tax Harvesting for Scheme: {scheme.name}")

    if scheme.type == EQUITY:
        if scheme.subtype == ELSS:
            num_days = 365 * 3
        else:
            num_days = 365
    else:
        logger.debug("Non-Equity Scheme - Skipping")
        return {}

    eligible_transactions_filter = get_transaction_older_than_filter(num_days)

    # Get transactions for active units
    active_purchase_transactions = get_purchase_transactions_for_active_units(scheme.transactions)

    # Get eligible purchase transactions
    eligible_purchase_transactions = get_filtered_transactions(
        eligible_transactions_filter, active_purchase_transactions
    )

    total_eligible_units = sum(
        [transaction.units for transaction in eligible_purchase_transactions]
    )
    approx_amount = total_eligible_units * scheme.nav
    approx_ltcg = Decimal("0.0")

    eligible_purchase_transactions = [
        transaction.dict() for transaction in eligible_purchase_transactions
    ]

    if total_eligible_units > 0:
        for transaction in eligible_purchase_transactions:
            profit_loss = (scheme.nav - transaction["nav"]) * transaction["units"]
            approx_ltcg += profit_loss
            transaction["P&L"] = profit_loss

    return {
        "scheme": scheme.name,
        "units": total_eligible_units,
        "nav": scheme.nav,
        "amount": approx_amount,
        "ltcg": approx_ltcg,
        "transactions": eligible_purchase_transactions,
    }


def get_valuation_summary_for_schemes(schemes: List[Scheme]):
    valuation = sum([scheme.valuation for scheme in schemes])
    schemes_details = [
        {
            "name": scheme.name,
            "valuation": scheme.valuation,
            "type": scheme.type,
            "subtype": scheme.subtype,
        }
        for scheme in schemes
    ]

    return {
        "valuation": valuation,
        "schemes": schemes_details,
    }
