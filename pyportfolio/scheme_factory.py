import datetime
from copy import deepcopy
from decimal import Decimal
from typing import List

from pydantic.error_wrappers import ValidationError


from casparser.types import CASParserDataType, SchemeType as CASParserSchemeType

from .models import Scheme
from .constants import EQUITY
from .mfhelper import get_scheme_details
from .utils import logger


def create_scheme_from_casparser(scheme_dict: CASParserSchemeType):
    scheme_dict = __update_scheme_details(scheme_dict)
    try:
        scheme_model = Scheme(**scheme_dict)
        return scheme_model
    except ValidationError as e:
        print(e)


def __update_scheme_details(scheme_dict: CASParserSchemeType):
    scheme_dict = deepcopy(scheme_dict)
    __update_transaction_details(scheme_dict)

    scheme_dict["units"] = scheme_dict["close_calculated"]
    scheme_dict["name"] = scheme_dict["scheme"]
    scheme_dict.pop("valuation")

    scheme_type, scheme_subtype, nav = None, None, None

    scheme_details = get_scheme_details(scheme_dict["amfi"])
    if scheme_details:
        nav = Decimal(scheme_details.get("nav"))
        scheme_type, scheme_subtype = scheme_details.get("scheme_category").split(" - ")
        if scheme_type == "Other Scheme":
            scheme_type = EQUITY

    scheme_dict["type"] = scheme_type
    scheme_dict["subtype"] = scheme_subtype
    scheme_dict["nav"] = nav

    return scheme_dict


def __update_transaction_details(scheme_dict: CASParserSchemeType):
    for transaction in scheme_dict["transactions"]:
        t_date = transaction["date"]
        transaction["days"] = (datetime.date.today() - t_date).days
        transaction["date"] = datetime.datetime(t_date.year, t_date.month, t_date.day)


def initialize_and_get_schemes(data_dict: CASParserDataType) -> List[Scheme]:
    schemes: List[Scheme] = []
    for folio in data_dict["folios"]:
        for scheme_dict in folio["schemes"]:
            scheme = create_scheme_from_casparser(scheme_dict)
            schemes.append(scheme)
            logger.debug(f"Done loading {scheme.name}")

    return schemes
