import json
from typing import Optional, Tuple

import pytest
from lxml.html import fromstring

from tests.utils import TEST_DATA_ROOT
from zyte_parsers.breadcrumbs import (
    Breadcrumb,
    _parse_breadcrumb_name,
    extract_breadcrumbs,
)


@pytest.mark.parametrize(
    ["name", "expected"],
    [
        (None, (None, None, None)),
        ("", (None, None, None)),
        (" ", (None, None, None)),
        (">", (">", None, None)),
        ("|", ("|", None, None)),
        ("->", ("->", None, None)),
        (" > ", (">", None, None)),
        (" >>> ", (">>>", None, None)),
        ("name", (None, "name", None)),
        ("some name", (None, "some name", None)),
        (" some name  ", (None, "some name", None)),
        ("  > some name  ", (">", "some name", None)),
        ("  >> some name  ", (">>", "some name", None)),
        ("  >some name  ", (None, ">some name", None)),
        (" some name > ", (None, "some name", ">")),
        (" some name >> ", (None, "some name", ">>")),
        ("> some name >> ", (">", "some name", ">>")),
        ("> > some name > >> ", (">", "> some name >", ">>")),
        (">    >> ", (">", None, ">>")),
        ("> > >", (">", ">", ">")),
    ],
)
def test_parsing_breadcrumbs_name(name, expected):
    result = _parse_breadcrumb_name(name)
    assert result == expected


@pytest.mark.parametrize(
    "item",
    json.loads(
        (TEST_DATA_ROOT / "breadcrumb_items_extract.json").read_text(encoding="utf8")
    ),
    ids=lambda item: f"[{item['snippet_path']}] - {item['base_url']}",
)
def test_extract_breadcrumbs(item):
    def print_breadcrumbs(breadcrumbs: Optional[Tuple[Breadcrumb, ...]]) -> None:
        if breadcrumbs is None:
            print("Breadcrumbs were not extracted")
        else:
            for b_item in breadcrumbs:
                print(b_item)

    if item.get("xfail"):
        pytest.xfail(item["xfail"])

    snippets_dir = TEST_DATA_ROOT / "breadcrumb_items_snippets"
    snippet_filename = item["snippet_path"]

    html = (snippets_dir / snippet_filename).read_text("utf8")

    node = fromstring(html)
    result = extract_breadcrumbs(node, base_url=item["base_url"])

    expected = tuple(Breadcrumb(**d) for d in item["expected"])

    print("Expected:")
    print_breadcrumbs(expected)
    print("Result:")
    print_breadcrumbs(result)
    assert expected == result
