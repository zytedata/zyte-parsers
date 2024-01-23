import copy
import re
from typing import List, Optional, Set
from urllib.parse import urlparse

from lxml.etree import strip_attributes
from lxml.html import HtmlElement, tostring

from .api import SelectorOrElement, input_to_element

# this is by far the most common, although 10 is also possible
# Some code below assumes it's 5 (with asserts in place).
BEST_RATING = 5

OF_STAR_PATTERNS = [
    r"^(\d+\.?\d*) stars",
    r"^(\d+\.?\d*) (out )?of 5 stars",
    r"^rated (\d+\.?\d*) (out )?of 5\b",
    r"\b(\d+\.?\d*) (out )?of 5\b",
    r"^(\d+\.?\d*)$",
]


def extract_rating_stars(node: SelectorOrElement) -> Optional[float]:
    """Extract a rating value from a node containing rating stars.

    :param node: Node that includes the rating stars.
    :return: Rating value as a float or None.
    """
    node = input_to_element(node)
    if any(_extract_rating_stars_nodes_quick_check(subnode) for subnode in node.iter()):
        node = copy.deepcopy(node)
        strip_attributes(node, "ng-class")

    extractions: Set[float] = set()
    for subnode in node.iter():
        extractions.update(
            extractor(subnode)  # type: ignore[misc]
            for extractor in [
                _extract_rating_stars_attrib,
                _extract_rating_stars_img,
                _extract_rating_stars_class,
                _extract_rating_stars_nodes,
                _extract_rating_stars_style_width,
            ]
        )
    extractions = {
        value
        for value in extractions
        if value is not None and 1 <= value <= BEST_RATING
    }

    if len(extractions) == 1:
        (value,) = extractions
        assert isinstance(value, float)
        return value

    if len(extractions) == 2:
        li_extractions: List[float] = sorted(extractions)
        if li_extractions[1] == BEST_RATING:
            value, _ = extractions
            assert isinstance(value, float)
            return value

    return None


def _extract_rating_stars_attrib(node: HtmlElement) -> Optional[float]:
    """Extract from title like "4 of out 5 stars"."""
    texts: List[str] = list(
        filter(
            None,
            (
                re.sub(r"\s+", " ", node.attrib.get(attrib, "")).lower().strip()
                for attrib in ["title", "alt", "aria-label"]
            ),
        )
    )
    assert BEST_RATING == 5
    for pattern in OF_STAR_PATTERNS:
        for text in texts:
            match = re.search(pattern, text)
            if match:
                return float(match.groups()[0])
    return None


def _extract_rating_stars_img(node: HtmlElement) -> Optional[float]:
    """Extract from the image name."""
    src = node.attrib.get("src", "").strip()
    if not src or src.startswith("data:"):
        return None
    name = urlparse(src).path.rsplit("/", 1)[-1]
    return _single_like_a_number(name)


def _single_like_a_number(text: str) -> Optional[float]:
    """Things similar to numbers in file names and URLs."""
    # 5.0, 5-0, 5_0, 50 are all fine
    numbers = re.findall(r"\d+[.\-_,]?\d*", text)
    if len(numbers) == 1:
        value = float(numbers[0].replace("-", ".").replace("_", ".").replace(",", "."))
        assert BEST_RATING == 5  # for below heuristics
        if value in {20, 30, 40, 50}:  # 10 is ambiguous, could be 10/10
            # FIXME 10 exclusion is a bit problematic as it creates a bias,
            # but any approach would have some bias, and it looks rare enough.
            value /= 10
        return value
    return None


N_CHILD_STARS = BEST_RATING


def _extract_rating_stars_nodes_quick_check(node: HtmlElement) -> bool:
    """Quick check whether an element might contain stars encoded as html."""
    children = list(node)
    if len(children) != N_CHILD_STARS:
        return False
    if len({ch.tag for ch in children}) != 1:
        return False
    return True


def _extract_rating_stars_nodes(node: HtmlElement) -> Optional[float]:
    """Look for N_CHILD_STARS children,
    first N of one kind and rest of another kind.
    """
    if not _extract_rating_stars_nodes_quick_check(node):
        return None
    children = list(node)
    child_ids = [tostring(ch, encoding="unicode").strip() for ch in children]
    if len(set(child_ids)) == 1:
        return float(N_CHILD_STARS)
    # this is quadratic but it's fine with low number of stars
    for n in range(1, N_CHILD_STARS):
        first, last = set(child_ids[:n]), set(child_ids[n:])
        if len(first) == len(last) == 1 and first != last:
            return float(n)
    return None


def _extract_rating_stars_class(node: HtmlElement) -> Optional[float]:
    """Extract rating from html class"""
    matches = set()
    for cls in node.attrib.get("class", "").lower().split():
        if "star" in cls or "rate" in cls or "rating" in cls:
            number = _single_like_a_number(cls)
            if number is not None and 1 <= number <= BEST_RATING:
                matches.add(number)
    if len(matches) == 1:
        (match,) = matches
        return match
    return None


def _extract_rating_stars_style_width(node: HtmlElement) -> Optional[float]:
    """Extract based on 'style="width:60%"' inline style."""
    style = node.attrib.get("style", "").lower().replace(" ", "")
    assert BEST_RATING == 5
    for rating, width in enumerate([20, 40, 60, 80, 100], 1):
        if f"width:{width}%" in style:
            return float(rating)
    return None
