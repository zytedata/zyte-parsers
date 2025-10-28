from __future__ import annotations

import itertools
from typing import TYPE_CHECKING

from .api import input_to_element
from .utils import extract_text, iterwalk_limited, take

if TYPE_CHECKING:
    from collections.abc import Iterable

    from lxml.html import HtmlElement

    from . import SelectorOrElement


def extract_brand_name(node: SelectorOrElement, search_depth: int = 0) -> str | None:
    """Extract a brand name from a node that contains it.

    It tries element text and image alt and title attributes.

    :param node: Node including the brand name.
    :param search_depth: Max depth for searching images.
    :return: The brand name or None.
    """
    _BRAND_LENGHT_LIMIT = 50

    node = input_to_element(node)
    extracted = _extract_brand(node, search_depth)
    short = (b for b in extracted if b and len(b) < _BRAND_LENGHT_LIMIT)
    results = take(short, 1)

    return results[0] if results else None


def _extract_brand(node: HtmlElement, search_depth: int = 0) -> Iterable[str | None]:
    if node.tag == "img":
        return extract_image_text(node, 0)
    value = extract_text(node)
    if value:
        return [value]
    return extract_image_text(node, search_depth)


def extract_image_text(node: HtmlElement, search_depth: int = 0) -> Iterable[str]:
    def extract_text_from_image(node: HtmlElement) -> Iterable[str | None]:
        for attrib in ["alt", "title"]:
            yield (node.attrib.get(attrib) or "").strip()

    nodes = iterwalk_limited(node, search_depth)
    images = filter(lambda n: n.tag == "img", nodes)
    attribs = map(extract_text_from_image, images)
    flat_attribs = itertools.chain.from_iterable(attribs)
    return (a for a in flat_attribs if a)
