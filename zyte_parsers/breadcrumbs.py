import re
import string
from collections import Counter
from typing import List, Optional, Tuple

import attr

from .api import InputType, input_to_element
from .utils import extract_link, extract_text, first_satisfying


@attr.s(frozen=True, auto_attribs=True)
class Breadcrumb:
    name: Optional[str] = None
    url: Optional[str] = None


_PUNCTUATION_TRANS = str.maketrans("", "", string.punctuation)
_BREADCRUMBS_SEP = (
    "ᐊᐅ<>ᐸᐳ‹›≺≻≪≫«»⋘⋙❬❭❮❯❰❱⟨⟩⟪⟫⫷⫸〈〉《》⦉⦊⭅⭆⭠⭢←→↤↦⇐⇒⇠⇢"
    "⇦⇨⇽⇾⟵⟶⟸⟹⟻⟼⟽⟾⮘⮚⮜⮞⯇⯈⊲⊳◀▶◁▷◂▸◃▹◄►◅▻➜➝➞➟➠➡➢➣➤➧➨➩"
    "➪➫➬➭➮➯➱➲/⁄\\⟋⟍⫻⫼⫽|𐬻¦‖∣⎪⎟⎸⎹│┃┆┇┊┋❘❙❚.,+:-"
)
SEP_REG_STR = rf"([{_BREADCRUMBS_SEP}]+|->)"

SPLIT_REG = re.compile(rf"(^|\s+)[{_BREADCRUMBS_SEP}]+($|\s+)")
SEP_REG = re.compile(rf"^{SEP_REG_STR}$")
LSTRIP_SEP_REG = re.compile(rf"^{SEP_REG_STR}\s+")
RSTRIP_SEP_REG = re.compile(rf"\s+{SEP_REG_STR}$")


def extract_breadcrumbs(
    node: InputType, *, base_url: Optional[str], max_search_depth: int = 10
) -> Optional[Tuple[Breadcrumb, ...]]:
    """Extract breadcrumb items from node that represents breadcrumb component.

    It finds all anchor elements to specified maximal depth. Anchors are
    collected in pre-order traversal. Such strategy of traversing supports
    cases where structure of nodes representing breadcrumbs is flat,
    which means that breadcrumb's anchors are on the same depth of HTML
    structure and where breadcrumb items are nested, which means that element
    with next item can be a child of element with previous breadcrumb item.
    It also post-processes extracted breadcrumbs by using semantic markup or
    the location of breadcrumb separators.
    :param node: Node representing and including breadcrumb component.
    :param base_url: Base URL of site.
    :param max_search_depth: Max depth for searching anchors.
    :return: Tuple with breadcrumb items.
    """

    def extract_breadcrumbs_rec(
        node,
        search_depth,
        breadcrumbs_accum,
        markup_hier_accum,
        separators_accum,
        list_tag_occured,
        curr_markup_hier,
    ):
        """
        Traverse html tree and search for elements that represent breadcrumb
        items with maximal depth of searching equal to `max_search_depth`.
        It also extracts breadcrumb items from element's tails since it often
        happens that non-anchor items are placed without any surrounding
        element.
        Because breadcrumb elements may contain dropdowns, the function
        filters them out by doing the following:
        * does not go into nested HTML list elements (<ol> and <ul>).
        * does not go into any HTML list elements with classes that relate
        to drop down, like "dropdown", "drop-down", "DropDown", etc.
        For every found element it does the following clean-up:
        * extracts name of breadcrumb from element's text or `title` attribute.
        * name cannot be a single character with punctuation like "»" or "|".
        * is able to parse name and split it from separators.
        * breadcrumb item has to contain name or url.
        * relative URLs are joined with base URL.
        """
        if node.tag in {"button"}:
            return

        if node.tag == "a" or len(node) == 0:
            name = first_satisfying(
                [
                    extract_text(node),
                    node.get("title").strip() if node.get("title") else None,
                ]
            )
            url = extract_link(node, base_url)

            left_sep, parsed_name, right_sep = _parse_breadcrumb_name(name)
            if left_sep and separators_accum and not separators_accum[-1]:
                separators_accum[-1] = left_sep
            if parsed_name or url:
                breadcrumbs_accum.append(Breadcrumb(parsed_name, url))
                markup_hier_accum.append(curr_markup_hier)
                separators_accum.append(right_sep)
        else:
            is_list_tag = node.tag in {"ul", "ol"}
            skip_list_tag = is_list_tag and (
                _has_special_class(node.get("class")) or list_tag_occured
            )

            item_type = _extract_markup_type(node)

            if search_depth < max_search_depth and not skip_list_tag:
                for child in node:
                    new_hierarchy = list(curr_markup_hier)
                    if item_type:
                        new_hierarchy.append(item_type)

                    extract_breadcrumbs_rec(
                        child,
                        search_depth + 1,
                        breadcrumbs_accum,
                        markup_hier_accum,
                        separators_accum,
                        list_tag_occured=list_tag_occured or is_list_tag,
                        curr_markup_hier=new_hierarchy,
                    )

        if node.tail is not None:
            left_sep, parsed_name, right_sep = _parse_breadcrumb_name(node.tail)
            if left_sep and separators_accum and not separators_accum[-1]:
                separators_accum[-1] = left_sep
            if parsed_name:
                breadcrumbs_accum.append(Breadcrumb(name=parsed_name))
                markup_hier_accum.append(curr_markup_hier)
                separators_accum.append(right_sep)

    node = input_to_element(node)

    breadcrumbs: List[Breadcrumb] = []
    markup_hier: List[List[str]] = []
    separators: List[bool] = []
    extract_breadcrumbs_rec(
        node,
        0,
        breadcrumbs,
        markup_hier,
        separators,
        list_tag_occured=False,
        curr_markup_hier=[],
    )
    assert len(breadcrumbs) == len(markup_hier) == len(separators)

    return _postprocess_breadcrumbs(breadcrumbs, markup_hier, separators)


def _parse_breadcrumb_name(
    name: Optional[str],
) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """Split extracted name into left separator, clean name and right separator."""
    if name:
        stripped_name = name.strip()
        if SEP_REG.match(stripped_name):
            return stripped_name.strip(), None, None

        left_match = LSTRIP_SEP_REG.match(stripped_name)
        left_sep = left_match.group().strip() if left_match else None
        without_left_sep = (
            stripped_name[left_match.end() :] if left_match else stripped_name
        )

        if SEP_REG.match(without_left_sep):
            return left_sep, None, without_left_sep.strip()

        right_match = RSTRIP_SEP_REG.search(without_left_sep)
        right_sep = right_match.group().strip() if right_match else None
        name = (
            without_left_sep[: right_match.start()] if right_match else without_left_sep
        )

        return left_sep, name or None, right_sep
    return None, None, None


def _postprocess_breadcrumbs(breadcrumbs, markup_hier, separators):
    """
    Post-process breadcrumbs using the following procedures:
    * If there is only a single breadcrumb with name and without link, try to
    split the name into separate breadcrumb items.
    * If markup exists, then use it for selecting correct breadcrumb items.
    * Otherwise, use location of separators to determine which breadcrumb items
    are relevant and which not (if there is separator between two items then
    these two items are relevant).
    """
    if not breadcrumbs:
        return None

    if len(breadcrumbs) == 1 and breadcrumbs[0].name and not breadcrumbs[0].url:
        parts = (s.strip() for s in SPLIT_REG.split(breadcrumbs[0].name))
        return tuple(Breadcrumb(name=p) for p in parts if p)

    markup_exists = any(len(h) > 0 for h in markup_hier)

    if markup_exists:
        breadcrumbs = _postprocess_using_markup(breadcrumbs, markup_hier)
    else:
        breadcrumbs = _postprocess_using_separators(breadcrumbs, separators)

    return tuple(_remove_duplicated_first_and_last_items(breadcrumbs))


def _postprocess_using_markup(breadcrumbs, markup_hier):
    breadcrumb_indices_with_markup = [
        idx for idx, h in enumerate(markup_hier) if len(h) > 0
    ]
    first_with_markup = min(breadcrumb_indices_with_markup, default=-1)
    last_with_markup = max(breadcrumb_indices_with_markup, default=-1)

    # often the items without markup at the beginning and the end are
    # respectively home and product items
    indices_to_leave = {first_with_markup - 1, last_with_markup + 1}

    return [
        b
        for idx, (b, h) in enumerate(zip(breadcrumbs, markup_hier))
        if idx in indices_to_leave or len(h) > 0
    ]


def _postprocess_using_separators(breadcrumbs, separators):
    def prev_sep(idx):
        return separators[idx - 1] if 0 <= idx - 1 < len(separators) else None

    most_common_seps = Counter(filter(None, separators)).most_common()
    main_sep = most_common_seps[0][0] if most_common_seps else None

    if not main_sep:
        return breadcrumbs

    return [
        b
        for idx, (b, sep) in enumerate(zip(breadcrumbs, separators))
        if sep == main_sep or (prev_sep(idx) == main_sep)
    ]


def _extract_markup_type(node):
    def check_schema(name):
        for schema_attr in {"itemtype", "typeof"}:
            if name in node.get(schema_attr, "").lower():
                return True
        return False

    if check_schema("data-vocabulary.org/breadcrumb"):
        return "data-vocabulary"
    if check_schema("listitem"):
        return "schema"


def _remove_duplicated_first_and_last_items(breadcrumbs):
    """
    Remove "go back" urls from the beginning or the end of breadcrumb
    element.
    There is an assumption that there can be only one such url.
    First it tries to remove url at the beginning by checking if there
    is any other the same url in further breadcrumb items. If not, it
    checks the last url by comparing it with remaining urls.
    """
    first_url = breadcrumbs[0].url
    if first_url is not None and first_url in (b.url for b in breadcrumbs[1:] if b.url):
        return breadcrumbs[1:]
    last_url = breadcrumbs[-1].url
    if last_url is not None and last_url in (b.url for b in breadcrumbs[1:-1] if b.url):
        return breadcrumbs[:-1]
    return breadcrumbs


def _has_special_class(class_attr: str) -> bool:
    """
    Check if a given value of class attribute has a class that relates to
    drop down like "dropdown", "drop-down", "DropDown", etc.
    """
    if class_attr:
        return any(
            cls_name in c.translate(_PUNCTUATION_TRANS).lower().strip()
            for cls_name in {"dropdown", "actions"}
            for c in class_attr.split()
        )
    return False
