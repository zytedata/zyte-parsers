from typing import Union

from lxml.html import HtmlElement
from parsel import Selector

InputType = Union[Selector, HtmlElement]


def input_to_selector(node: InputType) -> Selector:
    if isinstance(node, Selector):
        return node
    return Selector(root=node)


def input_to_element(node: InputType) -> HtmlElement:
    if isinstance(node, HtmlElement):
        return node
    return node.root
