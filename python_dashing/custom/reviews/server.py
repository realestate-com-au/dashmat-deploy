from python_dashing.errors import MissingServerOption, PythonDashingError
from python_dashing.core_modules.base import ServerBase

import requests
import logging
import random
import json

log = logging.getLogger("custom.reviews.server")

class Server(ServerBase):
    def setup(self, **kwargs):
        errors = []
        for key in ("app_id", "itunes_country_code"):
            if key not in kwargs:
                errors.append(MissingServerOption(wanted=key, module="custom.reviews"))
            else:
                setattr(self, key, kwargs[key])

        available = ("au", )
        if self.itunes_country_code not in available:
            errors.append(PythonDashingError("Sorry, specified itunes country code not support", wanted=self.itunes_country_code, available=available))

        if errors:
            raise MissingServerOption(_errors=errors)

    @property
    def routes(self):
        yield "/reviews", self.reviews

    @property
    def update_registration(self):
        yield "#reviews", "/reviews", {"every": 60}

    @property
    def register_checks(self):
        yield "0 */3 * * *", self.make_stats

    def reviews(self):
        data = json.loads(self.get_string("reviews-{0}-{1}".format(self.app_id, self.itunes_country_code)).decode('utf-8'))
        comments = json.loads(self.get_string("reviews-{0}-{1}-comments".format(self.app_id, self.itunes_country_code)).decode('utf-8'))['userReviewList']

        nice_comments = [r['body'] for r in comments if r['rating'] > 3]
        random.shuffle(nice_comments)

        label = data['ariaLabelForRatings']
        total_num_ratings = data['ratingCount']
        total_num_reviews = data['totalNumberOfReviews']
        rating_list = list(zip(("5 stars", "4 stars", "3 stars", "2 stars", "1 stars"), data['ratingCountList']))

        current_version_label = data['currentVersion']['ariaLabelForRatings']
        current_version_rating_count = int(data['currentVersion']['ratingCount'])
        return "results.jade", {"label": label, "total_num_ratings": total_num_ratings, "total_num_reviews": total_num_reviews, "rating_list": rating_list, "current_version_rating_count": current_version_rating_count, "current_version_label": current_version_label, "nice_comments": nice_comments}

    def make_stats(self, time_since_last_check):
        url = "https://itunes.apple.com/{0}/customer-reviews/id{1}".format(self.itunes_country_code, self.app_id)
        headers = {}
        if self.itunes_country_code == "au":
            headers.update({"X-Apple-Store-Front": "143460,32"})
        params = {"dataOnly": "true", "displayable-kind": 11, "appVersion": "all"}
        data = json.loads(requests.get(url, headers=headers, params=params).content.decode('utf-8'))
        self.set_string("reviews-{0}-{1}".format(self.app_id, self.itunes_country_code), json.dumps(data))

        url = "https://itunes.apple.com/WebObjects/MZStore.woa/wa/userReviewsRow"
        endIndex = data['totalNumberOfReviews']
        params = {
              "id": self.app_id
            , "displayable-kind": 11
            , "startIndex": 0
            , "endIndex": endIndex
            , "sort": 1
            , "appVersion": "all"
            }
        data = json.loads(requests.get(url, headers=headers, params=params).content.decode('utf-8'))
        self.set_string("reviews-{0}-{1}-comments".format(self.app_id, self.itunes_country_code), json.dumps(data))

