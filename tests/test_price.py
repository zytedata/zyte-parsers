from decimal import Decimal

import pytest
from lxml.html import fromstring
from price_parser import Price

from zyte_parsers.price import extract_price


@pytest.mark.parametrize(
    ["html", "currency_hint", "expected"],
    [
        ("<p></p>", None, Price(None, None, None)),
        ("<p>23.5</p>", None, Price(Decimal(23.5), None, "23.5")),
        ("<p>$23.5</p>", None, Price(Decimal(23.5), "$", "23.5")),
        ("<p>23.5</p>", "USD", Price(Decimal(23.5), "USD", "23.5")),
        ("<p>$23.5</p>", "USD", Price(Decimal(23.5), "$", "23.5")),
        ("<p>£23.5</p>", "USD", Price(Decimal(23.5), "£", "23.5")),
        ("<p>23.5</p>", "<b>USD</b>", Price(Decimal(23.5), "USD", "23.5")),
        ("<p>23.5</p>", fromstring("<b>USD</b>"), Price(Decimal(23.5), "USD", "23.5")),
    ],
)
def test_price_simple(html, currency_hint, expected):
    result = extract_price(fromstring(html), currency_hint=currency_hint)
    assert result == expected
