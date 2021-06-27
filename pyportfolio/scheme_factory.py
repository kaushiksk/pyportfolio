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


def create_scheme_from_casparser(scheme_dict: CASParserSchemeType) -> Scheme:
    """Create an object of Scheme model from casparser data

    Args:
        scheme_dict (CASParserSchemeType): scheme dict from casparser

    Returns:
        Scheme: instance of Scheme model

    Raises:
        ValidationError is dict parsing into Scheme model fails
    """
    scheme_dict = __update_scheme_details(scheme_dict)
    try:
        scheme_model = Scheme(**scheme_dict)
        return scheme_model
    except ValidationError:
        print(
            "Dict validation failed. Make sure you are using casparser.read_cas_pdf with output = 'dict'"
        )
        raise


def __update_scheme_details(scheme_dict: CASParserSchemeType):
    """Update scheme dict from casparser with additional metadata

    Args:
        scheme_dict (CASParserSchemeType): scheme dict from casparser

    Returns:
        dict: copy of input dict with updated keys and values to conform to Scheme model
    """
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
    """Update every transaction with additional info
        - Adds a 'days' value denoting how old the transaction is
        - Transforms 'date' into datetime object to conform with Scheme model. This is to help export this data to Mongo which only supports datetime.

    Args:
        scheme_dict : opy of input dict with updated keys and values to conform to Scheme model
    """
    for transaction in scheme_dict["transactions"]:
        t_date = transaction["date"]
        transaction["days"] = (datetime.date.today() - t_date).days
        transaction["date"] = datetime.datetime(t_date.year, t_date.month, t_date.day)


def initialize_and_get_schemes(data_dict: CASParserDataType) -> List[Scheme]:
    """Process schemes in dict provided by casparser into instances of Scheme model

    Args:
        data_dict (CASParserDataType): data from casparser.read_cas_pdf

    Returns:
        List[Scheme]: List of instances of Scheme model corresponding to all schemes in provided data
    """
    schemes: List[Scheme] = []
    for folio in data_dict["folios"]:
        for scheme_dict in folio["schemes"]:
            scheme = create_scheme_from_casparser(scheme_dict)
            schemes.append(scheme)
            logger.debug(f"Done loading {scheme.name}")

    return schemes
