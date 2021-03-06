from dashmat.errors import MissingServerOption, DashMatError
from dashmat.core_modules.base import ServerBase

from input_algorithms import spec_base as sb
from input_algorithms.meta import Meta

import requests
import logging
import random
import json

log = logging.getLogger("custom.reviews.server")

class Server(ServerBase):
    def setup(self, **kwargs):
        kwargs = sb.set_options(
              app_id = sb.required(sb.string_or_int_as_string_spec())
            , itunes_country_code = sb.required(sb.string_choice_spec(["au"]))
            ).normalise(Meta({}, []), kwargs)

        for key, val in kwargs.items():
            setattr(self, key, val)

    @ServerBase.Route()
    def total_reviews(self, datastore, latest=False):
        key = "reviews-{0}-{1}".format(self.app_id, self.itunes_country_code)
        if latest:
            key = "{0}-latest".format(key)
        data = datastore.retrieve(key)

        label = data['ariaLabelForRatings']
        total_num_ratings = data['ratingCount']
        total_num_reviews = data.get('totalNumberOfReviews')
        rating_list = list(zip(("5 stars", "4 stars", "3 stars", "2 stars", "1 stars"), data['ratingCountList']))
        return {"label": label, "total_num_ratings": total_num_ratings, "total_num_reviews": total_num_reviews, "rating_list": rating_list}

    @ServerBase.Route()
    def current_reviews(self, datastore):
        return self.total_reviews(datastore, latest=True)

    @ServerBase.Route()
    def comments(self, datastore):
        comments = datastore.retrieve("reviews-{0}-{1}-comments".format(self.app_id, self.itunes_country_code))['userReviewList']

        nice_comments = [r['body'] for r in comments if r['rating'] > 3]
        random.shuffle(nice_comments)

        return {"nice_comments": nice_comments}

    @ServerBase.check_every("0 */3 * * *")
    def make_stats(self, time_since_last_check):
        url = "https://itunes.apple.com/{0}/customer-reviews/id{1}".format(self.itunes_country_code, self.app_id)
        headers = {}
        if self.itunes_country_code == "au":
            headers.update({"X-Apple-Store-Front": "143460,32"})
        params = {"dataOnly": "true", "displayable-kind": 11, "appVersion": "all"}
        data = json.loads(requests.get(url, headers=headers, params=params).content.decode('utf-8'))
        yield "reviews-{0}-{1}".format(self.app_id, self.itunes_country_code), data

        params = {"dataOnly": "true", "displayable-kind": 11, "appVersion": "latest"}
        data = json.loads(requests.get(url, headers=headers, params=params).content.decode('utf-8'))
        yield "reviews-{0}-{1}-latest".format(self.app_id, self.itunes_country_code), data['currentVersion']

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
        yield "reviews-{0}-{1}-comments".format(self.app_id, self.itunes_country_code), data

