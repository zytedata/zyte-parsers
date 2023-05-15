import pytest

from zyte_parsers.breadcrumbs import _parse_breadcrumb_name


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
