from lxml.html import fromstring

from zyte_parsers.brand import extract_brand_name


def test_extract_brand():
    root = fromstring(
        '<div id="brand">simple brand</div>'
        '<div id="wrapper">'
        '<img id="img-alt" alt="my alt brand" title="foo" src="image-alt.png"/>'
        '<IMG id="img-title" title="my title brand" src="image-title.png"/>'
        '<img id="img-bare" src="image-bare.png"/>'
        '<img id="img-long" alt="very LOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOONG brand" title="short brand"/>'
        "</div>"
    )

    def exa(xpath):
        return extract_brand_name(root.xpath(xpath)[0], search_depth=2)

    assert exa('//div[@id="brand"]') == "simple brand"
    assert exa('//img[@id="img-alt"]') == "my alt brand"
    assert exa('//img[@id="img-title"]') == "my title brand"
    assert exa('//img[@id="img-bare"]') is None
    assert exa('//div[@id="wrapper"]') == "my alt brand"
    assert exa('//img[@id="img-long"]') == "short brand"
