import pytest

from zyte_parsers.review import extract_review_count_from_text

REVIEW_COUNT_CASES = [
    ("(2)", 2),
    ("23 Reviews", 23),
    ("0 review(s)", 0),
    ("6", 6),
    ("0", 0),
    ("No Reviews Yet", None),
    ("Review count : 23", 23),
    ("4.5/5 (23 reviews)", 23),
    ("4 out of 5 based on 5 review", None),
    ("Rating: 4.5 (9 Reviews)", 9),
    ("Rating: 3.2 (34)", 34),
    ("Review(s) 12", 12),
    ("8 Review(s)", 8),
    ("8 avaliações", 8),
    ("(0 Reviews)", 0),
    ("60 ratings", 60),
    ("17 omdömen", 17),
    ("77369", 77369),
    ("Average Rating (86):", 86),
    ("You have not rated this yet", None),
    ("60 ratings", 60),
    ("6,000 ratings", 6000),
    ("13,237 ratings", 13237),
    ("4.5/5 (10,237)", 10237),
    ("rating, reviews : 10,237)", 10237),
    ("reviews : 10 237", 10237),
    ("10,23", None),
]


@pytest.mark.parametrize(["value", "expected"], REVIEW_COUNT_CASES)
def test_review_count_extraction(value, expected):
    assert expected == extract_review_count_from_text(value)
