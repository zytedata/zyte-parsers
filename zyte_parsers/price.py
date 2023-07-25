from typing import Optional

from price_parser import Price

from zyte_parsers import SelectorOrElement
from zyte_parsers.utils import extract_text


def extract_price(
    node: SelectorOrElement, *, currency_hint: Optional[str] = None
) -> Price:
    """Extract a price value from a node that contains it.

    :param node: Node including the price text.
    :param currency_hint: Currency hint for ``price-parser``.
    :return: The price value as a ``price_parser.Price`` object.
    """
    text = extract_text(node)
    return Price.fromstring(text, currency_hint=currency_hint)
