from typing import Callable

from .constants import DEBT, EQUITY
from .models import Scheme


SchemeFilterType = Callable[[Scheme], bool]


def get_scheme_type_filter(scheme_type: str) -> SchemeFilterType:
    def scheme_type_filter(scheme: Scheme):
        return scheme.type == scheme_type

    return scheme_type_filter


# Filters
debt_scheme_filter = get_scheme_type_filter(DEBT)
equity_scheme_filter = get_scheme_type_filter(EQUITY)
