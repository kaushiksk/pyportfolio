import datetime
from copy import deepcopy
from decimal import Decimal
from typing import List

from casparser.types import CASParserDataType, SchemeType, TransactionDataType

from .constants import *
from .mfhelper import get_scheme_details
from .transaction_filters import (get_transaction_older_than_filter,
                                  get_transaction_type_filter)
from .utils import logger, or_filter

# Filters
purchase_transaction_filter = or_filter(
    [get_transaction_type_filter(PURCHASE), get_transaction_type_filter(PURCHASE_SIP)]
)
redemption_transaction_filter = get_transaction_type_filter(REDEMPTION)
stampduty_transaction_filter = get_transaction_type_filter(MISC)


class Scheme:
    def __init__(self, scheme_dict: SchemeType) -> None:
        # Use casparser.read_cas_pdf with output = "dict"
        self.name: str = scheme_dict["scheme"]
        self.amfi_id: str = scheme_dict["amfi"]
        self.units = scheme_dict["close_calculated"]
        self.transactions: List[TransactionDataType] = scheme_dict["transactions"]
        self.__update_scheme_details()
        self.__update_transaction_details()

    def __update_scheme_details(self):
        scheme_type, scheme_subtype, nav = None, None, None

        scheme_details = get_scheme_details(self.amfi_id)
        if scheme_details:
            nav = Decimal(scheme_details.get('nav'))
            scheme_type, scheme_subtype = scheme_details.get('scheme_category').split(" - ")
            if scheme_type == "Other Scheme":
                scheme_type = EQUITY
        
        self.scheme_type = scheme_type
        self.scheme_subtype = scheme_subtype
        self.nav = nav

    def __update_transaction_details(self):
        for transaction in self.transactions:
            transaction["Days"] = (datetime.date.today() - transaction["date"]).days

    @property
    def valuation(self):
        return self.units * self.nav

    @property
    def is_equity(self):
        return self.scheme_type == EQUITY

    def get_filtered_transactions(self, filter_to_apply, transactions=None):
        """Apply filter on transactions and return the filtered list
        Use the passed transactions if present else use self.transactions
        """
        if transactions is not None:
            return list(filter(filter_to_apply, transactions))

        return list(filter(filter_to_apply, self.transactions))

    def analyze_ltcg_tax_harvesting(self):
        logger.debug(f"LTCG Tax Harvesting for Scheme: {self.name}")

        if self.scheme_type == EQUITY:
            if self.scheme_subtype == ELSS:
                num_days = 365 * 3
            else:
                num_days = 365
        else:
            logger.debug("Non-Equity Scheme - Skipping")
            return

        eligible_transactions_filter = get_transaction_older_than_filter(num_days)

        # Get transactions for active units
        active_purchase_transactions = self.get_purchase_transactions_for_active_units()

        # Get eligible purchase transactions
        eligible_purchase_transactions = self.get_filtered_transactions(
            eligible_transactions_filter, active_purchase_transactions
        )

        total_eligible_units = sum(
            [transaction["units"] for transaction in eligible_purchase_transactions]
        )
        approx_amount = total_eligible_units * self.nav
        approx_ltcg = Decimal('0.0')

        if total_eligible_units > 0:
            for transaction in eligible_purchase_transactions:
                transaction["P&L"] = (self.nav - transaction["nav"]) * transaction["units"]

            approx_ltcg = float(
                sum(
                    [
                        transaction["P&L"]
                        for transaction in eligible_purchase_transactions
                    ]
                )
            )
            eligible_purchase_transactions = list(
                    map(
                        lambda x: {
                            "Date": x["date"],
                            "Days": x["Days"],
                            "Amount": x["amount"],
                            "Units": x["units"],
                            "NAV": x["nav"],
                            "P&L": x["P&L"],
                        },
                        eligible_purchase_transactions,
                    )
                )            

        return {
                "scheme": self.name,
                "units": total_eligible_units,
                "nav": self.nav,
                "amount": approx_amount,
                "ltcg": approx_ltcg,
                "transactions": eligible_purchase_transactions
            }


    def get_purchase_transactions_for_active_units(self):
        redeemed_transactions = self.get_filtered_transactions(
            redemption_transaction_filter
        )

        if len(redeemed_transactions) > 0:
            total_redeemed_units = abs(
                sum([transaction["units"] for transaction in redeemed_transactions])
            )
        else:
            total_redeemed_units = Decimal("0.0")

        # Perform deepcopy to avoid modifying the source reference
        purchase_transactions = deepcopy(
            self.get_filtered_transactions(purchase_transaction_filter)
        )

        if total_redeemed_units == 0:
            return purchase_transactions

        computed_units = Decimal("0.0")

        # We keep deleting transactions from top until all redemptions are satisfied
        while len(purchase_transactions) > 0:
            computed_units += purchase_transactions[0]["units"]

            if computed_units <= total_redeemed_units:
                # All these units were extinguished during redemption
                purchase_transactions.pop(0)
            else:
                # Part of the units were extinguished
                purchase_transactions[0]["units"] = (
                    computed_units - total_redeemed_units
                )
                purchase_transactions[0]["amount"] = (
                    purchase_transactions[0]["units"] * purchase_transactions[0]["nav"]
                )
                break  # No more units were extinguished

        return purchase_transactions

def initialize_and_get_schemes(data_dict: CASParserDataType) -> List[Scheme]:
        schemes: List[Scheme] = []
        for folio in data_dict["folios"]:
            for scheme_dict in folio["schemes"]:
                scheme = Scheme(scheme_dict)
                schemes.append(scheme)
                logger.debug(f"Done loading {scheme.name}")
        
        return schemes

def get_valuation_summary_for_schemes(schemes: List[Scheme]):
    valuation = sum([scheme.valuation for scheme in schemes])
    schemes_details = [{"name": scheme.name, "valuation": scheme.valuation, "type": scheme.scheme_type, "subtype": scheme.scheme_subtype} for scheme in schemes]

    return {
        "valuation": valuation,
        "schemes": schemes_details,
    }
