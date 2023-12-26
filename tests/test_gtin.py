import pytest
from lxml.html import fromstring
from parsel import Selector

from zyte_parsers.gtin import Gtin, extract_gtin, extract_gtin_id, gtin_classification

GTIN_CLASSIFICATION_CASES = [
    ("978-1-933624-34-1", "isbn13"),
    ("978-1-933624-76-1", "isbn13"),
    ("	978-1-62544-118-8", "isbn13"),
    ("9781625441775", "isbn13"),
    ("978-1-62544-167-6", "isbn13"),
    ("ISBN: 978-1-62544-175-1", "isbn13"),
    ("978-0-9801023-6-9", "isbn13"),
    ("9780062315007", "isbn13"),
    ("978-1-56619-909-4 ", "isbn13"),
    # Negative examples for ISBN by changing last digit
    ("978-1-56619-909-5 ", None),
    ("978-1-56619-909-6 ", None),
    ("978-1-56619-909-70 ", None),
    ("978-1-56619-909 ", None),
    ("0-545-01022-5", "isbn10"),
    (" 1 86197 271-7", "isbn10"),
    ("7350053850019", "gtin13"),
    ("EAN: 8808993650040", "gtin13"),
    ("4015600608835", "gtin13"),
    ("4031778810191", "gtin13"),
    ("042100005264", "upc"),
    # Negative examples by changing last digit in above number
    ("042100005265", None),
    ("042100005266", None),
    ("042100005267", None),
    ("042100005268", None),
    # Test cases for ISSN
    ("03178471", "issn"),
    ("0083-2421", "issn"),
    ("0500-0270", "issn"),
    ("ISSN: 0500-0270", "issn"),
    ("1562-6865", "issn"),
    ("10637710", "issn"),
    # Negative examples by changing the last digit of the last number
    ("10637711", None),
    ("10637712", None),
    ("10637713", None),
    # Test cases for ISMN
    ("979-0-65001-268-3", "ismn"),
    ("9790035236338", "ismn"),
    ("9790035057292", "ismn"),
    # Negative examples for ismn
    ("979-0-65001-268-4", None),
    ("979-0-65001-268-5", None),
    ("979-0-65001-268-6", None),
    # Test cases from the annotated data
    ("978-2-89455-671-9", "isbn13"),
    ("9780285640856", "isbn13"),
    ("ISBN-13: 978-1607439677", "isbn13"),
    ("8590875345921", "gtin13"),
    ("4001868008067", "gtin13"),
    ("7897396607622", "gtin13"),
    ("857392003023", "upc"),
    ("4250586357265", "gtin13"),
    ("3661276011335", "gtin13"),
    ("(9782894556726)", "isbn13"),
    ("    0161019884293", "gtin13"),
    ("8717801048538", "gtin13"),
    ("9780285640856", "isbn13"),
    # Test cases for gtin14
    ("10614141543219", "gtin14"),
    ("0001 2345 6000 12", "gtin14"),
    ("4 07007 1967 072 0", "gtin14"),
    ("1061-4141-543-219", "gtin14"),
    ("gtin14: 10614141543219", "gtin14"),
    ("gtin: 09501101530003", "gtin14"),
    ("00075678164125", "gtin14"),
    # Negatvie test cases for gtin14
    ("10614141543218", None),
    ("10614141543217", None),
    ("10614141543216", None),
    ("10614141543215", None),
    ("00012345600013", None),
    ("00012345600014", None),
    ("00012345600015", None),
    ("00012345600016", None),
    # Test cases for gtin8 cases
    ("40170725", "gtin8"),
    (" gtin8 : 12345670", "gtin8"),
    ("(93123457)", "gtin8"),
    ("Gtin : 47612341", "gtin8"),
    ("59012344", "gtin8"),
    # Negative test cases for gtin8
    ("40170726", None),
    ("40170727", None),
    ("40170728", None),
    ("40170729", None),
    ("40170720", None),
]


@pytest.mark.parametrize(["value", "expected"], GTIN_CLASSIFICATION_CASES)
def test_gtin_classification(value, expected):
    assert expected == gtin_classification(value)


GTIN_IDS = [
    # Simple cases
    ("978-1-933624-34-1", "9781933624341"),
    ("978-1-933624-76-1", "9781933624761"),
    ("	978-1-62544-118-8", "9781625441188"),
    ("ISBN# 9781625441775", "9781625441775"),
    ("978-1-62544-167-6", "9781625441676"),
    ("ISBN: 978-1-62544-175-1", "9781625441751"),
    ("ISBN - 978-0-9801023-6-9", "9780980102369"),
    ("isbn 9780062315007", "9780062315007"),
    ("978-1-56619-909-4 ", "9781566199094"),
    ("EAN# 8808993650040", "8808993650040"),
    # More complex examples with ids where the numeric values
    # will pass the gtin checksum, however the non-numeric character
    # are intercepted in these, therefore, these should not be passed
    # as gtin ID.
    ("HD978193-INT3624341", None),
    ("TFG-05451-HOP-0225", None),
    ("1063HP7710", None),
    # Cases with the prefix having numeric values (eg. gtin13, isbn10)
    ("EAN13: 8808993650040", "8808993650040"),
    ("EAN13#8717801048538", "8717801048538"),
    ("EAN13 8808993650040", "8808993650040"),
    ("Isbn13: 978-1-62544-175-1", "9781625441751"),
    ("ISBN10: 0-545-01022-5", "0545010225"),
    ("ISBN10-0-545-01022-5", "0545010225"),
    ("ISBN10 0-545-01022-5", "0545010225"),
    ("Isbn-10: 0-545-01022-5", "0545010225"),
    # Cases with the prefix having numeric values and code starting with same
    # numeric prefix value (eg. gtin13 and code starting with 13 like 1334567890125)
    # Gtin14 startign with 14 (e.g. 14334567890129)
    ("EAN131334567890125", "1334567890125"),
    ("EAN1334567890125", "1334567890125"),
    ("Gtin13 1334567890125", "1334567890125"),
    ("Gtin 1334567890125", "1334567890125"),
    ("Gtin1414334567890129", "14334567890129"),
    ("Gtin14334567890129", "14334567890129"),
    # Example text cases
    ("TSF8UP-R407-26A44", None),
    ("978-2-89455-671-9", "9782894556719"),
    ("9780285640856", "9780285640856"),
    ("ISBN-13: 978-1607439677", "9781607439677"),
    ("8590875345921", "8590875345921"),
    ("(9782894556726)", "9782894556726"),
    # Example test cases from the real world product pages
    ("EAN:	9781101872239", "9781101872239"),
    ("ISBN:	0722539312", "0722539312"),
    ("UPC4960759145062", "4960759145062"),
    ("ISBN13: 9780525555360 ", "9780525555360"),
    ("ISBN10: 0525555366 ", "0525555366"),
    ("ISBN-13: 9780525576709", "9780525576709"),
    ("ISBN-10: 0525576703", "0525576703"),
    ("UPC:	884116293835", "884116293835"),
    ("8423490261447 -", "8423490261447"),
]


@pytest.mark.parametrize(["value", "expected"], GTIN_IDS)
def test_extract_gtin_id(value, expected):
    assert expected == extract_gtin_id(value)


GTINS = [
    ("TSF8UP-R407-26A44", None),
    ("978-1-933624-34-1", Gtin("isbn13", "9781933624341")),
]


@pytest.mark.parametrize(["value", "expected"], GTINS)
def test_extract_gtin(value, expected):
    assert expected == extract_gtin(fromstring(f"<p>{value}</p>"))


def test_extract_gtin_types():
    value = "978-1-933624-34-1"
    expected = Gtin("isbn13", "9781933624341")
    assert expected == extract_gtin(value)
    assert expected == extract_gtin(fromstring(f"<p>{value}</p>"))
    assert expected == extract_gtin(Selector(text=f"<p>{value}</p>"))
