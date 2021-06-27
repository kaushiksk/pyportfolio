import casparser
import sys
from casparser.exceptions import CASParseError
from typing import List

from .scheme_utils import (
    analyze_ltcg_tax_harvesting,
    get_valuation_summary_for_schemes,
    get_filtered_schemes,
)
from .scheme_filters import debt_scheme_filter, equity_scheme_filter
from .scheme_factory import initialize_and_get_schemes
from .models import Scheme
from .utils import logger


class Portfolio:
    def __init__(self, cas_file, cas_password) -> None:
        logger.info("Parsing CAS File")

        try:
            data = casparser.read_cas_pdf(cas_file, cas_password)
        except CASParseError as e:
            logger.error(e)
            logger.error("Aborting!")
            sys.exit()

        self.investor_info = data["investor_info"]

        logger.info("Loading schemes in portfolio")
        self.schemes: List[Scheme] = initialize_and_get_schemes(data)

    def ltcg_tax_harvesting_summary(self):
        equity_schemes = get_filtered_schemes(equity_scheme_filter, self.schemes)
        tax_harvesting_opportunities = [
            analyze_ltcg_tax_harvesting(scheme) for scheme in equity_schemes
        ]
        tax_harvesting_opportunities = list(
            filter(lambda x: x["ltcg"] != 0, tax_harvesting_opportunities)
        )
        total_ltcg = sum([x["ltcg"] for x in tax_harvesting_opportunities])
        total_amount = sum([x["amount"] for x in tax_harvesting_opportunities])

        return {
            "total_ltcg": total_ltcg,
            "total_amount": total_amount,
            "schemes": tax_harvesting_opportunities,
        }

    def get_valuation_summary(self):
        debt_schemes = get_filtered_schemes(debt_scheme_filter, self.schemes)
        equity_schemes = get_filtered_schemes(equity_scheme_filter, self.schemes)

        debt_valuation = get_valuation_summary_for_schemes(debt_schemes)
        equity_valuation = get_valuation_summary_for_schemes(equity_schemes)

        return {
            "valuation": debt_valuation["valuation"] + equity_valuation["valuation"],
            "debt_valuation": debt_valuation,
            "equity_valuation": equity_valuation,
        }

    def to_dict(self):
        return {
            "user_info": self.investor_info,
            "schemes": [scheme.dict() for scheme in self.schemes],
            "valuation": sum([scheme.valuation for scheme in self.schemes]),
        }
