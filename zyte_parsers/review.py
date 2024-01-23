import re
from typing import Optional

from price_parser.parser import parse_number

from .api import SelectorOrElement, input_to_element
from .utils import extract_text


def extract_review_count(node: SelectorOrElement) -> Optional[int]:
    """Extract review count from a node containing it.

    :param node: Node that includes the review count.
    :return: Review count as an int or None.
    """
    node = input_to_element(node)
    node_text = extract_text(node)
    review_count = extract_review_count_from_text(node_text)
    return review_count


def extract_review_count_from_text(node_text: Optional[str]) -> Optional[int]:
    """
    Extracts reviewCount from the text. If the text consists of single number then
    it is returned as reviewCount. If the text consists of more than one numbers
    and one number if present in brackets() then this number is extracted as the
    reviewCount e.g. ("4.5/5 (4 reviews)"). Other ambiguous cases are ignored.
    """
    if not node_text:
        return None
    review_count_regex = r"\d+?,\d+|\d+? \d+|\d+"
    review_counts = re.findall(review_count_regex, node_text)
    bracket_content = re.search(r"\((.*?)\)", node_text)
    if len(review_counts) == 1:
        return normalize_to_int(review_counts[0])
    if len(review_counts) > 1 and bracket_content:
        # Sometime text consist of both rating and review count
        # Eg. 4.5/5 (2 reviews)
        # Extract the text from brackets in such cases
        bracket_text = bracket_content.group(1)
        review_counts = re.findall(review_count_regex, bracket_text)
        if len(review_counts) == 1:
            return normalize_to_int(review_counts[0])
    return None


def normalize_to_int(review_count_text: str) -> Optional[int]:
    count_decimal = parse_number(review_count_text)
    if count_decimal is None:
        return None
    return int(count_decimal) if count_decimal == int(count_decimal) else None
