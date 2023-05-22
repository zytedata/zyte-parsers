from typing import Union

from lxml.html import HtmlElement
from parsel import Selector

SelectorOrElement = Union[Selector, HtmlElement]


def input_to_selector(node: SelectorOrElement) -> Selector:
    if isinstance(node, Selector):
        return node
    return Selector(root=node)


def input_to_element(node: SelectorOrElement) -> HtmlElement:
    if isinstance(node, HtmlElement):
        return node
    return node.root
