Changes
=======

0.5.0 (2024-01-24)
------------------

* Add the ``extract_rating`` and ``extract_rating_stars`` functions for
  extracting values.
* Add the ``extract_review_count`` function for extracting review counts.

0.4.0 (2023-12-26)
------------------

* New dependencies:

  * ``gtin-validator >= 1.0.3``
  * ``python-stdnum >= 1.19``
  * ``six``

* Add the ``extract_gtin`` function for extracting GTIN values of various
  types.
* Add support for text input to ``extract_price``.
* Add support for Python 3.12.
* CI improvements.

0.3.0 (2023-07-28)
------------------

* Now requires ``price-parser >= 0.3.4``.
* Add the ``extract_price`` function for extracting prices and currencies.

0.2.0 (2023-07-07)
------------------

* Add the ``extract_brand_name`` function for extracting brands.
* Drop Python 3.7 support.

0.1.1 (2023-05-24)
------------------

* Fix building documentation.

0.1.0 (2023-05-24)
------------------

* Initial version.
* Includes extraction of ``Breadcrumb`` objects.
