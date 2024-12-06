import itertools
from typing import Any, Callable, Iterable, Optional
from urllib.parse import urljoin, urlparse, urlunparse

import html_text
from lxml.html import (  # noqa: F401
    HtmlComment,
    HtmlElement,
    fragment_fromstring,
    fromstring,
)
from parsel import Selector  # noqa: F401
from w3lib.html import strip_html5_whitespace
from w3lib.url import safe_url_string

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


def add_https_to_url(url: str) -> str:
    if url.startswith(("http://", "https://")):
        return url

    parsed_url = urlparse(url)
    if not parsed_url.scheme and parsed_url.netloc:
        parsed_url = parsed_url._replace(scheme="https")

    return str(urlunparse(parsed_url))


def extract_link(
    a_node: SelectorOrElement, base_url: str, force_safe=False
) -> Optional[str]:
    """
    Extract the absolute url link from an ``<a>`` HTML tag.
    """
    a_node = input_to_element(a_node)
    link = a_node.get("href") or a_node.get("data-url")

    if not link or is_js_url(link):
        return None

    try:
        link = strip_urljoin(base_url, link)
    except ValueError:
        link = None

    if not force_safe:
        return link

    try:
        safe_link = safe_url_string(link)
    except ValueError:
        return None

    # add scheme (https) when missing schema and no base url
    safe_link = add_https_to_url(safe_link)

    return safe_link


def extract_text(
    node: Optional[SelectorOrElement], guess_layout: bool = False
) -> Optional[str]:
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


def iterwalk_limited(node: HtmlElement, search_depth: int) -> Iterable[HtmlElement]:
    yield node

    if search_depth <= 0:
        return

    for child in node:
        yield from iterwalk_limited(child, search_depth - 1)


def take(iterable: Iterable[Any], n: int):
    return list(itertools.islice(iterable, n))
