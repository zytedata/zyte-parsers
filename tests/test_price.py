from decimal import Decimal

import pytest
from lxml.html import fromstring

from zyte_parsers.price import extract_price


@pytest.mark.parametrize(
    ["html", "expected"],
    [
        ("<p></p>", None),
        ("<p>23.5</p>", Decimal(23.5)),
        ("<p>$23.5</p>", Decimal(23.5)),
    ],
)
def test_price_simple(html, expected):
    result = extract_price(fromstring(html))
    assert result == expected
