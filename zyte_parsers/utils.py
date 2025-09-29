from __future__ import annotations

import itertools
from typing import TYPE_CHECKING, Callable, TypeVar
from urllib.parse import urljoin

import html_text
from lxml.html import (  # noqa: F401
    HtmlComment,
    HtmlElement,
    fragment_fromstring,
    fromstring,
)
from parsel import Selector  # noqa: F401
from w3lib.html import strip_html5_whitespace

from zyte_parsers.api import SelectorOrElement, input_to_element

if TYPE_CHECKING:
    from collections.abc import Iterable


_T = TypeVar("_T")


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
    return bool(url.strip().lower().startswith(("javascript:", "#")))


def strip_urljoin(base_url: str | None, url: str | None) -> str:
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


def extract_link(a_node: SelectorOrElement, base_url: str | None) -> str | None:
    """
    Extract the absolute url link from an ``<a>`` HTML tag.

    >>> extract_link(fromstring("<a href=' http://example.com'></a>"), "")
    'http://example.com'
    >>> extract_link(fromstring("<a href='/foo '></a>"), "http://example.com")
    'http://example.com/foo'
    >>> extract_link(fromstring("<a href='' data-url='http://example.com'></a>"), "")
    'http://example.com'
    >>> extract_link(fromstring("<a href='javascript:void(0)'></a>"), "")
    >>> extract_link(Selector(text="<a href='http://example.com'></a>").css("a")[0], "")
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


def extract_text(
    node: SelectorOrElement | None, guess_layout: bool = False
) -> str | None:
    """Extract text from HTML using ``html_text``.

    >>> extract_text(fromstring("<p>foo  bar </p>"))
    'foo bar'
    >>> extract_text(Selector(text="<p>foo  bar </p>"))
    'foo bar'
    >>> extract_text(fragment_fromstring("<!-- a comment -->"))
    >>> extract_text(Selector(text="<!-- a comment -->"))
    """
    if node is None:
        return None
    node = input_to_element(node)
    if isinstance(node, HtmlComment):
        return None
    value = html_text.extract_text(node, guess_layout=guess_layout)
    if value:
        return value
    return None


def first_satisfying(
    xs: Iterable[_T],
    condition_fun: Callable[[_T], bool] = lambda x: bool(x),
    default: _T | None = None,
) -> _T | None:
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


def iterwalk_limited(node: HtmlElement, search_depth: int) -> Iterable[HtmlElement]:
    yield node

    if search_depth <= 0:
        return

    for child in node:
        yield from iterwalk_limited(child, search_depth - 1)


def take(iterable: Iterable[_T], n: int) -> list[_T]:
    return list(itertools.islice(iterable, n))
