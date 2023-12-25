import re
from typing import Optional, Union

import attr
from gtin.validator import is_valid_GTIN
from stdnum import isbn, ismn, issn

from . import SelectorOrElement
from .utils import extract_text


@attr.s(frozen=True, auto_attribs=True)
class Gtin:
    type: str
    value: str


GTIN_MATCH_SPECIAL_CHARACTER_REGEX = re.compile(r"[^0-9a-zA-Z]")
GTIN_MATCH_NON_NUMERIC_REGEX = re.compile(r"[^0-9]")

# Consider only those prefix which have some numeric values as these
# values interfere with the gtin id extraction
GTIN_PREFIX = [
    "isbn13",
    "isbn10",
    "ean13",
    "gtin8",
    "gtin12",
    "gtin13",
    "gtin14",
]
GTIN_PREFIX_REGEX = re.compile("|".join(GTIN_PREFIX), re.IGNORECASE)
GTIN_CENTER_REGEX = re.compile(r"^\D*|\D*$")


def extract_gtin(node: Union[SelectorOrElement, str]) -> Optional[Gtin]:
    """Extract a GTIN (Global Trade Item Number) from a node or a string that contains its text.

    It detects the GTIN type and returns it together with the cleaned GTIN
    value. The following types are supported: `isbn10`, `isbn13`, `issn`,
    `ismn`, `upc`, `gtin8`, `gtin13`, `gtin14`.

    :param node: A node or a string that includes the GTIN text.
    :return: A GTIN item.
    """
    gtin: Optional[str]
    if isinstance(node, str):
        gtin = node
    else:
        gtin = extract_text(node)
    gtin_id = extract_gtin_id(gtin)
    gtin_class = gtin_classification(gtin_id)
    if gtin_class:
        assert isinstance(gtin_id, str)
        return Gtin(gtin_class, gtin_id)
    return None


def _remove_gtin_numeric_prefix(gtin_code: str) -> str:
    """
    The function removes the gtin specific numeric prefix from the gtin text if
    length after prefix removal is the expected length for that prefix.
    E.g. ean13 is a prefix with a numeric value 13 in it. Text ean13 is removed only
    if after removal the length of numeric code is 13. It is done in order to avoid cases
    where we by mistake might remove the digits 13 from the actual gtin code.
    """
    prefix_match = GTIN_PREFIX_REGEX.search(gtin_code)
    if prefix_match:
        prefix = prefix_match.group()
        s, e = prefix_match.span()
        gtin_without_prefix = gtin_code[:s] + gtin_code[e:]
        gtin_expected_len = int(GTIN_MATCH_NON_NUMERIC_REGEX.sub("", prefix))
        numeric_code_without_prefix = GTIN_MATCH_NON_NUMERIC_REGEX.sub(
            "", gtin_without_prefix
        )
        if len(numeric_code_without_prefix) == gtin_expected_len:
            return gtin_without_prefix
    return gtin_code


def extract_gtin_id(gtin_code: Optional[str]) -> Optional[str]:
    """
    The function extracts the gtin_id from the text. For text like
    'EAN13: 7350053850019', first 'EAN13' is extracted then the gtin_id is
    extracted. For some tricky sku values like 'TSF8UP-R407-26A44' if we only
    remove non-numeric values we end up with number like '84072644' which is
    classified as gtin (issn), therefore, we also check that the gtin_id does
    not contain any letter between the numeric values.
    """
    if gtin_code:
        gtin_id_alphanum = GTIN_MATCH_SPECIAL_CHARACTER_REGEX.sub("", gtin_code)
        gtin_id_suffix = _remove_gtin_numeric_prefix(gtin_id_alphanum)
        gtin_center = GTIN_CENTER_REGEX.sub("", gtin_id_suffix)
        gtin_id = GTIN_MATCH_NON_NUMERIC_REGEX.sub("", gtin_center)
        if gtin_id == gtin_center:
            return gtin_id
    return None


def gtin_classification(gtin: Optional[str]) -> Optional[str]:
    """
    The function performs gtin classification for the gtin code.
    The gtin classification is performed based on a number of rules associated
    with the different gtin categories. The categories considered here for gtin
    classification are :
     -isbn10
     -isbn13
     -issn
     -ismn
     -upc
     -ean13
    Return: gtin_class(str) if a class is found else None
    """
    gtin = extract_gtin_id(gtin)
    if not gtin:
        return None

    try:
        ismn_validity = ismn.validate(gtin)
    except Exception:
        ismn_validity = False

    if ismn_validity:
        return "ismn"

    try:
        isbn_validity = isbn.validate(gtin)
    except Exception:
        isbn_validity = False

    if isbn_validity and len(gtin) == 10:
        return "isbn10"

    if isbn_validity and len(gtin) == 13:
        return "isbn13"

    try:
        issn_validity = issn.validate(gtin)
    except Exception:
        issn_validity = False

    if issn_validity:
        return "issn"

    gtin_valid = is_valid_GTIN(gtin)

    if gtin_valid and len(gtin) == 8:
        return "gtin8"

    if gtin_valid and len(gtin) == 14:
        return "gtin14"

    if gtin_valid and len(gtin) == 13:
        return "gtin13"

    if gtin_valid and len(gtin) == 12:
        return "upc"

    return None
