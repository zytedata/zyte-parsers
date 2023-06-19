import re
from math import isnan
from typing import Any, List, Optional

import attr
from lxml.html import HtmlElement

from .api import SelectorOrElement, input_to_element
from .utils import extract_text


@attr.s(frozen=True, auto_attribs=True)
class AggregateRating:
    bestRating: Optional[float] = None
    ratingValue: Optional[float] = None


POSSIBLE_BEST_RATINGS = {4.0, 5.0, 6.0, 10.0, 20.0, 100.0}


def extract_rating(node: SelectorOrElement) -> AggregateRating:
    """Extract rating data from a node.

    :param node: Node that includes the rating data.
    :return: AggregateRating item.
    """
    node = input_to_element(node)
    node_text = extract_text(node)
    rating_value = None
    best_rating = None
    if node_text is None:
        return AggregateRating(ratingValue=rating_value, bestRating=best_rating)
    node_nums = _get_rating_numbers(node_text)
    if len(node_nums) == 2:
        rating_value = node_nums[0]
        best_rating = node_nums[1]
    elif len(node_nums) == 1:
        rating_value = node_nums[0]
        assert isinstance(rating_value, float)
        best_rating = _extract_best_rating_tail_or_next(node, rating_value)
    elif len(node_nums) > 2:
        rating_value = node_nums[0]
    return AggregateRating(ratingValue=rating_value, bestRating=best_rating)


def _check_best_rating(value: float, rating_value: float) -> Optional[float]:
    """
    Function checks the bestRating value takes a valid value from one of the
    preselected set of values and is less than ratingValue.
    >>> _check_best_rating(5.0, 4.0)
    5.0
    >>> _check_best_rating(5.0, 8.0) is None
    True
    >>> _check_best_rating(86.0, 4.0) is None
    True
    >>> _check_best_rating(22.43, 4.0) is None
    True
    """
    best_rating = (
        value if value >= rating_value and value in POSSIBLE_BEST_RATINGS else None
    )
    return best_rating


def _get_rating_numbers(node_text: Optional[str]) -> List[Optional[float]]:
    rating_nums: List = []
    if node_text:
        node_nums = re.findall(r"\d*,\d+|\d*\.\d+|\d+", node_text)
        rating_nums = [
            n_rating
            for n_rating in map(_normalize_rating, node_nums)
            if n_rating is not None
        ]
    return rating_nums


def _extract_best_rating_tail_or_next(
    node: HtmlElement, rating_value: float
) -> Optional[float]:
    best_rating_text_candidates = [node.tail, extract_text(node.getnext())]
    for best_rating_text in best_rating_text_candidates:
        rating_nums = _get_rating_numbers(best_rating_text)
        if len(rating_nums) > 0:
            best_rating = rating_nums[0]
            assert isinstance(best_rating, float)
            return _check_best_rating(best_rating, rating_value)
    return None


def _remove_nan_from_float(val: Optional[float]) -> Optional[float]:
    return val if isinstance(val, float) and not isnan(val) else None


def _str_to_float(rating: str) -> Optional[float]:
    try:
        return float(rating)
    except ValueError:
        return None


def _normalize_rating(rating_val: Any) -> Optional[float]:
    if isinstance(rating_val, str):
        # convert values like 4,5 to 4.5
        rating_val = rating_val.replace(",", ".")
        rating_val = _str_to_float(rating_val)
    elif isinstance(rating_val, (int, float)):
        # convert int average rating value to float
        rating_val = float(rating_val)
    else:
        rating_val = None
    rating_val = _remove_nan_from_float(rating_val)
    return rating_val
