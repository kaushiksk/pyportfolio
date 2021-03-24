from typing import List
from scheme import Scheme, initialize_and_get_schemes
import casparser
from constants import EQUITY, DEBT
from utils import logger

debt_scheme_filter = lambda scheme: scheme.scheme_type == DEBT
equity_scheme_filter = lambda scheme: scheme.scheme_type == EQUITY

class Portfolio:
    def __init__(self, cas_file, cas_password) -> None:
        logger.info("Parsing CAS File")
        data = casparser.read_cas_pdf(cas_file, cas_password)
        
        self.investor_info = data["investor_info"]

        logger.info("Loading schemes in portfolio")
        self.schemes = initialize_and_get_schemes(data)
    
    def get_debt_schemes(self):
        return self.__get_filtered_schemes(debt_scheme_filter)
    
    def get_equity_schemes(self):
        return self.__get_filtered_schemes(equity_scheme_filter)
    
    def ltcg_tax_harvesting_summary(self):
        equity_schemes = self.get_equity_schemes()
        tax_harvesting_opportunities = [scheme.analyze_ltcg_tax_harvesting() for scheme in equity_schemes]
        tax_harvesting_opportunities = list(filter(lambda x: x["ltcg"] != 0, tax_harvesting_opportunities))
        total_ltcg = sum([x["ltcg"] for x in tax_harvesting_opportunities])
        total_amount = sum([x["amount"] for x in tax_harvesting_opportunities])

        return {
            "total_ltcg": total_ltcg,
            "total_amount": total_amount,
            "schemes": tax_harvesting_opportunities,
        }
    
    def __get_filtered_schemes(self, filter_to_apply) -> List[Scheme]:
         return list(filter(filter_to_apply, self.schemes))