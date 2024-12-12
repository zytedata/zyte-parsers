from pathlib import Path

import pytest
from parsel import Selector  # noqa: F401

from zyte_parsers.utils import extract_link, fromstring

TEST_DATA_ROOT = Path(__file__).parent / "data"


@pytest.mark.parametrize(
    "html_input, base_url, expected_output",
    [
        ("<a href=' http://example.com'>", "", "http://example.com"),
        ("<a href='foo'>", "http://example.com", "http://example.com/foo"),
        ("<a href='/foo '>", "http://example.com", "http://example.com/foo"),
        ("<a href='//foo '>", "http://example.com", "http://foo"),
        (
            "<a href='//example.com/foo'>",
            "http://example.com",
            "http://example.com/foo",
        ),
        # Selector
        (
            Selector(text="<a href='http://example.com'>").css("a")[0],
            "",
            "http://example.com",
        ),
        # no base url
        ("<a href='foo'>", "", "foo"),
        ("<a href='/foo '>", "", "/foo"),
        ("<a href='//foo '>", "", "//foo"),
        ("<a href='' data-url='http://example.com'>", "", "http://example.com"),
        ("<a href='http://example.com'>", "", "http://example.com"),
        # invalid url
        ("<a href='javascript:void(0)'>", "", None),
        ("<a href=''>", "http://example.com", None),
    ],
)
def test_extract_link(html_input, base_url, expected_output):
    a_node = fromstring(html_input) if isinstance(html_input, str) else html_input
    result = extract_link(a_node, base_url)
    assert result == expected_output


@pytest.mark.parametrize(
    "html_input, base_url, expected_output",
    [
        # Spaces in the path
        (
            "<a href='/path/to/resource with spaces'>",
            "http://example.com",
            "http://example.com/path/to/resource%20with%20spaces",
        ),
        # Missing schema and base_url
        (
            "<a href='//example.com/foo'>",
            "",
            "//example.com/foo",
        ),
        # no base url
        ("<a href='foo'>", "", "foo"),
        ("<a href='/foo '>", "", "/foo"),
        ("<a href='//foo '>", "", "//foo"),
        ("<a href='' data-url='http://example.com'>", "", "http://example.com"),
        ("<a href='http://example.com'>", "", "http://example.com"),
    ],
)
def test_extract_safe_link(html_input, base_url, expected_output):
    a_node = fromstring(html_input) if isinstance(html_input, str) else html_input
    result = extract_link(a_node, base_url, force_safe=True)
    assert result == expected_output
