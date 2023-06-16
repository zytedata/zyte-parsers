from lxml.html import fromstring

from zyte_parsers.brand import Brand, extract_brand


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
        return extract_brand(root.xpath(xpath)[0], search_depth=2)

    assert exa('//div[@id="brand"]') == Brand("simple brand")
    assert exa('//img[@id="img-alt"]') == Brand("my alt brand")
    assert exa('//img[@id="img-title"]') == Brand("my title brand")
    assert exa('//img[@id="img-bare"]') is None
    assert exa('//div[@id="wrapper"]') == Brand("my alt brand")
    assert exa('//img[@id="img-long"]') == Brand("short brand")
