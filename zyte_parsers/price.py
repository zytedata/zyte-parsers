from decimal import Decimal
from typing import Optional

from price_parser import Price

from zyte_parsers import SelectorOrElement
from zyte_parsers.utils import extract_text


def extract_price(node: SelectorOrElement) -> Optional[Decimal]:
    """Extract a price value from a node that contains it.

    :param node: Node including the price text.
    :return: The price value or None.
    """
    text = extract_text(node)
    price_parsed = Price.fromstring(text)
    return price_parsed.amount
