from typing import Optional
from urllib.parse import urljoin

import html_text
from w3lib.html import strip_html5_whitespace

from zyte_parsers.api import SelectorOrElement, input_to_element


def is_js_url(url: str) -> bool:
    normed = url.strip().lower()
    if normed.startswith("javascript:") or normed.startswith("#"):
        return True
    return False


def strip_urljoin(base_url: Optional[str], url: Optional[str]) -> str:
    """urljoin with stripping whitespace from url, since url can have
    extra spaces and resulting URL wrong.
    """
    if url is not None:
        url = strip_html5_whitespace(url)
    # XXX: mypy doesn't like when one passes None to urljoin
    return urljoin(base_url or "", url or "")


def extract_link(a_node: SelectorOrElement, base_url: str) -> Optional[str]:
    """
    Extracts the absolute url link form a ``<a>`` HTML tag.
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
    node = input_to_element(node)
    value = html_text.extract_text(node, guess_layout=guess_layout)
    if value:
        return value
    return None


def first_satisfying(xs, condition_fun=lambda x: x, default=None):
    try:
        return next(x for x in xs if condition_fun(x))
    except StopIteration:
        return default
