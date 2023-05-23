from typing import Any, Callable, Iterable, Optional
from urllib.parse import urljoin

import html_text
from lxml.html import fromstring  # noqa: F401
from parsel import Selector  # noqa: F401
from w3lib.html import strip_html5_whitespace

from zyte_parsers.api import SelectorOrElement, input_to_element


def is_js_url(url: str) -> bool:
    """Check if the URL is intended for handling by JS.

    >>> is_js_url("http://example.com")
    False
    >>> is_js_url("/foo")
    False
    >>> is_js_url("javascript:void(0)")
    True
    >>> is_js_url("#")
    True
    """
    normed = url.strip().lower()
    if normed.startswith("javascript:") or normed.startswith("#"):
        return True
    return False


def strip_urljoin(base_url: Optional[str], url: Optional[str]) -> str:
    r"""Strip the URL and use ``urljoin`` on it.

    >>> strip_urljoin("http://example.com", None)
    'http://example.com'
    >>> strip_urljoin("http://example.com", "foo")
    'http://example.com/foo'
    >>> strip_urljoin("http://example.com", "  ")
    'http://example.com'
    >>> strip_urljoin("http://example.com", " foo\t")
    'http://example.com/foo'
    >>> strip_urljoin(None, "foo")
    'foo'
    >>> strip_urljoin(None, None)
    ''
    """
    if url is not None:
        url = strip_html5_whitespace(url)
    # XXX: mypy doesn't like when one passes None to urljoin
    return urljoin(base_url or "", url or "")


def extract_link(a_node: SelectorOrElement, base_url: str) -> Optional[str]:
    """
    Extract the absolute url link from an ``<a>`` HTML tag.

    >>> extract_link(fromstring("<a href=' http://example.com'"), "")
    'http://example.com'
    >>> extract_link(fromstring("<a href='/foo '"), "http://example.com")
    'http://example.com/foo'
    >>> extract_link(fromstring("<a href='' data-url='http://example.com'"), "")
    'http://example.com'
    >>> extract_link(fromstring("<a href='javascript:void(0)'"), "")
    >>> extract_link(Selector(text="<a href='http://example.com'").css("a")[0], "")
    'http://example.com'
    """
    a_node = input_to_element(a_node)
    link = a_node.get("href") or a_node.get("data-url")

    if not link or is_js_url(link):
        return None

    try:
        link = strip_urljoin(base_url, link)
    except ValueError:
        link = None

    return link


def extract_text(node: SelectorOrElement, guess_layout: bool = False) -> Optional[str]:
    """Extract text from HTML using ``html_text``.

    >>> extract_text(fromstring("<p>foo  bar </p>"))
    'foo bar'
    >>> extract_text(Selector(text="<p>foo  bar </p>"))
    'foo bar'
    """
    node = input_to_element(node)
    value = html_text.extract_text(node, guess_layout=guess_layout)
    if value:
        return value
    return None


def first_satisfying(
    xs: Iterable, condition_fun: Callable[[Any], Any] = lambda x: x, default: Any = None
) -> Any:
    """Return the first item in ``xs`` that satisfies the condition.

    >>> first_satisfying([0, "", 1])
    1
    >>> first_satisfying([1, 2, 3], condition_fun=lambda x: x > 1)
    2
    >>> first_satisfying([0, ""], default=2)
    2
    """
    try:
        return next(x for x in xs if condition_fun(x))
    except StopIteration:
        return default
