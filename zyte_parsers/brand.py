import itertools
from typing import Iterable, Optional

import attr
from lxml.html import HtmlElement

from . import SelectorOrElement
from .api import input_to_element
from .utils import extract_text, iterwalk_limited, take


@attr.s(frozen=True, auto_attribs=True)
class Brand:
    name: str


def extract_brand(node: SelectorOrElement, search_depth: int = 0) -> Optional[Brand]:
    """Extract a brand name from a node that contains it.

    It tries element text and image alt and title attributes.

    :param node: Node including the brand name.
    :param search_depth: Max depth for searching images.
    :return: A Brand item.
    """
    _BRAND_LENGHT_LIMIT = 50

    node = input_to_element(node)
    extracted = _extract_brand(node, search_depth)
    short = (b for b in extracted if b and len(b) < _BRAND_LENGHT_LIMIT)
    results = take(short, 1)

    return Brand(results[0]) if results else None


def _extract_brand(node: HtmlElement, search_depth: int = 0) -> Iterable[Optional[str]]:
    if node.tag == "img":
        return extract_image_text(node, 0)
    value = extract_text(node)
    if value:
        return [value]
    return extract_image_text(node, search_depth)


def extract_image_text(node: HtmlElement, search_depth: int = 0) -> Iterable[str]:
    def extract_text_from_image(node: HtmlElement) -> Iterable[Optional[str]]:
        for attrib in ["alt", "title"]:
            yield (node.attrib.get(attrib) or "").strip()

    nodes = iterwalk_limited(node, search_depth)
    images = filter(lambda n: n.tag == "img", nodes)
    attribs = map(extract_text_from_image, images)
    flat_attribs = itertools.chain.from_iterable(attribs)
    valid_attribs = (a for a in flat_attribs if a)

    return valid_attribs
