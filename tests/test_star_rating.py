import pytest
from lxml.html import fromstring

from zyte_parsers.star_rating import extract_rating_stars

RATING_STARS_TEST_CASES = [
    {
        "expected": 3,
        "html": """
        <span class="stamped-starratings stamped-review-header-starratings">
          <i class="stamped-fa stamped-fa-star "></i>
          <i class="stamped-fa stamped-fa-star "></i>
          <i class="stamped-fa stamped-fa-star "></i>
          <i class="stamped-fa stamped-fa-star-o "></i>
          <i class="stamped-fa stamped-fa-star-o "></i>
        </span>
        """,
    },
    {
        "expected": 5,
        "html": """
        <span class="stamped-starratings stamped-review-header-starratings">
          <i class="stamped-fa stamped-fa-star "></i>
          <i class="stamped-fa stamped-fa-star "></i>
          <i class="stamped-fa stamped-fa-star "></i>
          <i class="stamped-fa stamped-fa-star "></i>
          <i class="stamped-fa stamped-fa-star "></i>
        </span>
        """,
    },
    {
        "expected": 5,
        "html": """
        <div class="review-stars">
          <i class="icon-star-full"></i>
          <i class="icon-star-full"></i>
          <i class="icon-star-full"></i>
          <i class="icon-star-full"></i>
          <i class="icon-star-full"></i>
        </div>
        """,
    },
    {
        "expected": 4,
        "html": """
        <div>
          <div class="review-stars">
            <i class="icon-star-full"></i>
            <i class="icon-star-full"></i>
            <i class="icon-star-full"></i>
            <i class="icon-star-full"></i>
            <i class="icon-star-empty"></i>
          </div>
        </div>
        """,
    },
    {
        "expected": None,
        "html": """
        <div class="review-stars">
          <i class="icon-star-full"></i>
          <i class="icon-star-empty"></i>
          <i class="icon-star-full"></i>
          <i class="icon-star-full"></i>
          <i class="icon-star-full"></i>
        </div>
        """,
    },
    {
        "expected": 4,
        "html": """
        <div aria-hidden="true" class="pr-rating-stars">
          <div class="pr-star-v4 pr-star-v4-100-filled"></div>
          <div class="pr-star-v4 pr-star-v4-100-filled"></div>
          <div class="pr-star-v4 pr-star-v4-100-filled"></div>
          <div class="pr-star-v4 pr-star-v4-100-filled"></div>
          <div class="pr-star-v4 pr-star-v4-0-filled"></div>
        </div>
        """,
    },
    {
        "expected": 5,
        "html": """
        <img src="/mas_assets//reviews/stars_5.0.png" style="vertical-align:text-bottom;">
        """,
    },
    {
        "expected": 4,
        "html": """
        <img src="/mas_assets//reviews/stars_4.0.png" style="vertical-align:text-bottom;">
        """,
    },
    {
        "expected": 2,
        "html": """
        <img src="/mas_assets//reviews/stars_2.0.png" style="vertical-align:text-bottom;">
        """,
    },
    {
        "expected": 5,
        "html": """
        <span style="white-space: nowrap">
          <span class="sa_star sa_activestar"></span>
          <span class="sa_star sa_activestar"></span>
          <span class="sa_star sa_activestar"></span>
          <span class="sa_star sa_activestar"></span>
          <span class="sa_star sa_activestar"></span>
        </span>
        """,
    },
    {
        "expected": 5,
        "html": """
        <div class="review-rating">
          <img src="https://cdn2.bigcommerce.com/server3400/e4mezc/templates/__custom/images/icon-rating-large5.png?t=1549483962" alt="">
        </div>
        """,
    },
    {
        "expected": 4,
        "html": """
        <div class="review-rating">
          <img src="https://cdn2.bigcommerce.com/server3400/e4mezc/templates/__custom/images/icon-rating-large4.png?t=1549483962" alt="">
        </div>
        """,
    },
    {
        "expected": 5,
        "html": """
        <img src="images/stars_5.gif" alt="5 of 5 Stars!" title=" 5 of 5 Stars! " border="0">
        """,
    },
    {
        "expected": None,
        "html": """
        <img src="images/stars_56786.gif">
        """,
    },
    {
        "expected": None,
        "html": """
        <img src="images5/stars.gif">
        """,
    },
    {
        "expected": 4,
        "html": """
        <img src="images/stars_5.gif" title="4 of 5 Stars!">
        """,
    },
    {
        "expected": 4,
        "html": """
        <div class="review_stars" title="4 stars">
          <div style="width:80%">
          <meta itemprop="reviewRating" content="4"></div>
        </div>
        """,
    },
    {
        "expected": 5,
        "html": """
        <div class="review_stars" title="5 stars">
            <div style="width:100%">
            <meta itemprop="reviewRating" content="5"></div>
        </div>
        """,
    },
    {
        "expected": 5,
        "html": """
        <div class="ReviewStars">
          <div class="FullStarWrapper">
            <svg class="FullStar" xmlns="https://www.w3.org/2000/svg" viewBox="0 0 100 100"><polygon points="50.18 1.44 63.97 35.23 100.36 37.9 72.48 61.45 81.2 96.89 50.18 77.66 19.17 96.89 27.88 61.45 0 37.9 36.4 35.23 50.18 1.44"></polygon></svg>
            <svg class="FullStar" xmlns="https://www.w3.org/2000/svg" viewBox="0 0 100 100"><polygon points="50.18 1.44 63.97 35.23 100.36 37.9 72.48 61.45 81.2 96.89 50.18 77.66 19.17 96.89 27.88 61.45 0 37.9 36.4 35.23 50.18 1.44"></polygon></svg>
            <svg class="FullStar" xmlns="https://www.w3.org/2000/svg" viewBox="0 0 100 100"><polygon points="50.18 1.44 63.97 35.23 100.36 37.9 72.48 61.45 81.2 96.89 50.18 77.66 19.17 96.89 27.88 61.45 0 37.9 36.4 35.23 50.18 1.44"></polygon></svg>
            <svg class="FullStar" xmlns="https://www.w3.org/2000/svg" viewBox="0 0 100 100"><polygon points="50.18 1.44 63.97 35.23 100.36 37.9 72.48 61.45 81.2 96.89 50.18 77.66 19.17 96.89 27.88 61.45 0 37.9 36.4 35.23 50.18 1.44"></polygon></svg>
            <svg class="FullStar" xmlns="https://www.w3.org/2000/svg" viewBox="0 0 100 100"><polygon points="50.18 1.44 63.97 35.23 100.36 37.9 72.48 61.45 81.2 96.89 50.18 77.66 19.17 96.89 27.88 61.45 0 37.9 36.4 35.23 50.18 1.44"></polygon></svg>
          </div>
          <div class="HalfStarWrapper"></div>
          <div class="EndStarWrapper"></div>
        </div>
        """,
    },
    {
        "expected": 4,
        "html": """
        <span class="bv-rating-stars-container">
          <abbr title="4 out of 5 stars." class="bv-rating bv-rating-stars bv-rating-stars-off" aria-hidden="true"> ★★★★★ </abbr>
          <abbr title="4 out of 5 stars." style="width:80% !important;" class="bv-rating-max bv-rating-stars bv-rating-stars-on" aria-hidden="true"> ★★★★★ </abbr>
          <span class="bv-off-screen">4 out of 5 stars.</span>
        </span>
        """,
    },
    {
        "expected": 5,
        "html": """
        <span class="bv-rating-stars-container">
          <abbr title="5 out of 5 stars." class="bv-rating bv-rating-stars bv-rating-stars-off" aria-hidden="true"> ★★★★★ </abbr>
          <abbr title="5 out of 5 stars." style="width:100% !important;" class="bv-rating-max bv-rating-stars bv-rating-stars-on" aria-hidden="true"> ★★★★★ </abbr>
          <span class="bv-off-screen">5 out of 5 stars.</span>
        </span>
        """,
    },
    {
        "expected": 5,
        "html": """
        <div class="pr-stars pr-stars-small pr-stars-5-sm" title="Perfect. It doesn't get any better"> </div>
        """,
    },
    {
        "expected": 4,
        "html": """
        <div class="star-rating" title="Rated 4 out of 5">
        """,
    },
    {
        "expected": 1,
        "html": """
        <i class="orange rate-1" aria-hidden="true"></i>
        """,
    },
    {
        "expected": 4,
        "html": """
        <div class="sheet-section__comment-stars star-4"></div>
        """,
    },
    {
        "expected": 3,
        "html": """
        <div class="rateit bigstars" aria-label="customer rated this 3 out of 5">
          <div class="rateit-range">
            <div class="rateit-selected rateit-preset"></div>
          </div>
        </div>
        """,
    },
    {
        "expected": 5,
        "html": """
        <div aria-hidden="true" role="radiogroup" class="pr-rating-stars">
        <div role="radio" class="pr-star-v4 pr-star-v4-100-filled" aria-checked="true" tabindex="-1"></div>
        <div role="radio" class="pr-star-v4 pr-star-v4-100-filled" aria-checked="true" tabindex="-1"></div>
        <div role="radio" class="pr-star-v4 pr-star-v4-100-filled" aria-checked="true" tabindex="-1"></div>
        <div role="radio" class="pr-star-v4 pr-star-v4-100-filled" aria-checked="true" tabindex="-1"></div>
        <div role="radio" class="pr-star-v4 pr-star-v4-100-filled" aria-checked="true" tabindex="-1"></div>
        </div>
        """,
    },
    {
        "expected": 4,
        "html": """
        <div class="stars">
          <i class="icon-star gold"></i>
          <i class="icon-star gold" ng-class="{gold:review.rating&gt;1}"></i>
          <i class="icon-star gold" ng-class="{gold:review.rating&gt;2}"></i>
          <i class="icon-star gold" ng-class="{gold:review.rating&gt;3}"></i>
          <i class="icon-star" ng-class="{gold:review.rating&gt;4}"></i>
        </div>
        """,
    },
    {
        "expected": 5,
        "html": """
        <ol aria-hidden="true" class="star-rating__list star-rating--filled-5.0">
        """,
    },
    {
        "expected": 4.5,
        "html": """
        <ol class="star-rating__list star-rating--filled-4,5">
        """,
    },
    {
        "expected": 4.5,
        "html": """
        <ol class="star-rating__list star-rating--filled-4_5">
        """,
    },
    {
        "expected": 5,
        "html": """
        <span class="rating ">
          <span style="width: 100%"></span>
        </span>

        """,
    },
    {
        "expected": 3,
        "html": """
        <span class="star-rating__gold review-rating-star" style="width:60%"></span>
        """,
    },
    {
        "expected": 4,
        "html": """
        <img src="data:image/svg+xml;base64,..." alt="star" title="4">
        """,
    },
    {
        "expected": 5,
        "html": """
        <span class="stars-container" tabindex="" aria-label="5.0 Stars. 0 reviews.">
        """,
    },
    {
        "expected": 3,
        "html": """
        <div class="TTratingBox TTrating-3-0">
        """,
    },
    {
        "expected": 5,
        "html": """
        <div role="img" class="ebay-star-rating">
          <span class="star-rating">
            <i class="fullStar"></i>
            <i class="fullStar"></i>
            <i class="fullStar"></i>
            <i class="fullStar"></i>
            <i class="fullStar"></i>
          </span>
        </div>
        """,
    },
    {
        "expected": 5,
        "html": """
        <div class="stars stars50" style="height:initial"><span class="f24 fc3" style="padding-left:10px"> </span></div>
        """,
    },
    {
        "expected": 4,
        "html": """
        <div class="rating" style="width:80%">
        <div class="relative whitespace-no-wrap inline-block text-sm" style="width:95px; height:21px;">
        <div class="absolute">
          <i class="fa fa-star text-primary-light-v1"></i><i class="fa fa-star text-primary-light-v1"></i><i class="fa fa-star text-primary-light-v1"></i>
          <i class="fa fa-star text-primary-light-v1"></i><i class="fa fa-star text-primary-light-v1"></i>
        </div>
        <div class="absolute overflow-hidden" style="width:80%">
          <i class="fa fa-star text-primary-v1"></i><i class="fa fa-star text-primary-v1"></i><i class="fa fa-star text-primary-v1"></i>
          <i class="fa fa-star text-primary-v1"></i><i class="fa fa-star text-primary-v1"></i>
        </div>
        </div>
        """,
    },
    {
        "expected": 1,
        "xfail": True,
        "html": """
        <div aria-hidden="true" class="pr-rating-stars">
          <div class="pr-star-v4 pr-star-v4-100-filled"></div>
          <div class="pr-star-v4 pr-star-v4-0-filled"></div>
          <div class="pr-star-v4 pr-star-v4-0-filled"></div>
          <div class="pr-star-v4 pr-star-v4-0-filled"></div>
          <div class="pr-star-v4 pr-star-v4-0-filled"></div>
          <span class="pwrStarCont" style="position: relative !important;">
            <span class="pwrStar_top" style="width:27px !important"></span>
            <span class="pwrStar_bottom"></span>
          </span>
        </div>
        """,
    },
]


@pytest.mark.parametrize("case", RATING_STARS_TEST_CASES)
def test_extract_rating_stars(case):
    if case.get("xfail"):
        pytest.xfail()
    node = fromstring(case["html"])
    value = extract_rating_stars(node)
    assert value == case["expected"]
