from __future__ import annotations

from typing import Union, cast

from lxml.html import HtmlComment, HtmlElement
from parsel import Selector

SelectorOrElement = Union[Selector, HtmlElement, HtmlComment]


def input_to_selector(node: SelectorOrElement) -> Selector:
    """Convert a supported input object to a Selector."""
    if isinstance(node, Selector):
        return node
    return Selector(root=node)


def input_to_element(node: SelectorOrElement) -> HtmlElement | HtmlComment:
    """Convert a supported input object to a HtmlElement or HtmlComment."""
    if isinstance(node, (HtmlElement, HtmlComment)):
        return node
    return cast("HtmlElement | HtmlComment", node.root)
