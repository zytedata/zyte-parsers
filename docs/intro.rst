=====
Intro
=====

``zyte-parsers`` provides functions that extract specific data from HTML
elements. The input element can be an instance of either
:class:`parsel.selector.Selector` or :class:`lxml.html.HtmlElement`. Some
functions can also take a string with text (e.g. extracted from HTML or JSON)
as input.

.. autoclass:: zyte_parsers.SelectorOrElement

Parsers
=======

Brand
-----

.. autofunction:: zyte_parsers.extract_brand_name

Breadcrumbs
-----------

.. autoclass:: zyte_parsers.Breadcrumb
   :members:
   :undoc-members:

.. autofunction:: zyte_parsers.extract_breadcrumbs

GTIN
----

.. autoclass:: zyte_parsers.Gtin
   :members:
   :undoc-members:

.. autofunction:: zyte_parsers.extract_gtin

Price
-----

.. autofunction:: zyte_parsers.extract_price

Ratings and review count
------------------------

.. autoclass:: zyte_parsers.AggregateRating
   :members:
   :undoc-members:

.. autofunction:: zyte_parsers.extract_rating
.. autofunction:: zyte_parsers.extract_rating_stars
.. autofunction:: zyte_parsers.extract_review_count
