from typing import Union

from lxml.html import HtmlElement
from parsel import Selector

SelectorOrElement = Union[Selector, HtmlElement]


def input_to_selector(node: SelectorOrElement) -> Selector:
    """Convert a supported input object to a Selector."""
    if isinstance(node, Selector):
        return node
    return Selector(root=node)


def input_to_element(node: SelectorOrElement) -> HtmlElement:
    """Convert a supported input object to a HtmlElement."""
    if isinstance(node, HtmlElement):
        return node
    return node.root
