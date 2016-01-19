from dashmat.core_modules.amazon_base.server import ServerMixin
from dashmat.core_modules.base import ServerBase
from dashmat.errors import DashMatError

from input_algorithms import spec_base as sb
from input_algorithms.meta import Meta

from six.moves import zip_longest
from itertools import chain
import calendar
import requests
import datetime
import logging
import json

log = logging.getLogger("custom.scaling.server")

class Server(ServerBase, ServerMixin):
    def setup(self, **kwargs):
        account_spec = sb.set_options(
              account_id = sb.required(sb.string_spec())
            , role_to_assume = sb.required(sb.string_spec())
            )

        kwargs = sb.set_options(
              accounts = sb.required(sb.dictof(sb.string_spec(), account_spec))
            , ordered_accounts = sb.required(sb.listof(sb.string_spec()))
            , cloudability_auth_token = sb.required(sb.any_spec())
            ).normalise(Meta({}, []), kwargs)

        for key, val in kwargs.items():
            setattr(self, key, val)

    @property
    def cloudability_auth(self):
        if not getattr(self, "_cloudability_auth", None):
            self._cloudability_auth = self.cloudability_auth_token
            if callable(self._cloudability_auth):
                self._cloudability_auth = self._cloudability_auth()
        return self._cloudability_auth

    @property
    def routes(self):
        yield "cost_last_month", lambda ds: self.cost(ds, this_month=False)
        yield "cost_this_month", lambda ds: self.cost(ds, this_month=True)

        yield "scaling", self.scaling
        yield "instance_count", self.instance_counts

    def cost(self, datastore, this_month=True):
        by_account = []

        for name in self.ordered_accounts:
            options = self.accounts[name]
            data = datastore.retrieve("scaling-{0}".format(options["account_id"]))
            by_account.append((name, data['cost'][this_month]))

        return {"cost": by_account}

    def instance_counts(self, datastore):
        by_account = []

        for name in self.ordered_accounts:
            options = self.accounts[name]
            data = datastore.retrieve("scaling-{0}".format(options["account_id"]))
            by_account.append((name, data))
        return {"instance_counts": by_account}

    def scaling(self, datastore):
        by_account = []
        applications = {}

        for name in self.ordered_accounts:
            options = self.accounts[name]
            data = datastore.retrieve("scaling-{0}".format(options["account_id"]))

            by_account.append((name, options["account_id"]))
            for scaling_options in data['autoscaling']:
                if scaling_options['name'] not in applications:
                    applications[scaling_options['name']] = {}
                applications[scaling_options['name']][name] = scaling_options

        applications = list(reversed(sorted(applications.items(), key= lambda item: self.ordered_accounts[-1] in item[1])))
        return {"applications": applications, "by_account": by_account}

    @property
    def register_checks(self):
        def named(name):
            def ret(func):
                func.__name__ = name
                return func
            return ret

        make_statser = lambda name, options: named(name)(lambda t: self.make_stats(options))
        for name in self.ordered_accounts:
            options = self.accounts[name]
            yield "*/5 * * * *", make_statser(name, options)

    def make_stats(self, options):
        session = self.make_boto_session(options["account_id"], options["role_to_assume"])
        ec2 = session.client("ec2", "ap-southeast-2")
        terminated = lambda instance: instance["State"]["Name"] in ("terminated", "shutting-down")

        total_num_dead_instances = 0
        total_num_alive_instances = 0
        for instance in chain.from_iterable([reservations['Instances'] for reservations in ec2.describe_instances()["Reservations"]]):
            if instance["State"]["Name"] in ("termianted", "shutting-down"):
                total_num_dead_instances += 1
            else:
                total_num_alive_instances += 1

        found = []
        autoscaling = session.client("autoscaling", "ap-southeast-2")
        for group in autoscaling.describe_auto_scaling_groups()["AutoScalingGroups"]:
            name = [tag["Value"] for tag in group["Tags"] if tag["Key"] == "aws:cloudformation:stack-name"][0]
            desired_capacity = group['DesiredCapacity']

            num_dead_instances = 0
            num_alive_instances = 0
            for instance in group["Instances"]:
                if instance['LifecycleState'] == "InService":
                    num_alive_instances += 1
                else:
                    num_dead_instances += 1

            found.append({"alive": num_alive_instances, "dead": num_dead_instances, "desired": desired_capacity, "name": name })

        log.info("Finding cost from cloudability for {0}".format(options["account_id"]))
        cost = self.cost_from_cloudability(options["account_id"])
        yield "scaling-{0}".format(options["account_id"]), {"dead": total_num_dead_instances, "alive": total_num_alive_instances, "autoscaling": found, "cost": cost}

    def cost_from_cloudability(self, account):
        today = datetime.datetime.utcnow().date()
        this_month = [datetime.date(year=today.year, month=today.month, day=1), today]
        if today.month == 1:
            first_of_last_month = datetime.date(year=today.year-1, month=1, day=1)
        else:
            first_of_last_month = datetime.date(year=today.year, month=today.month-1, day=1)
        last_month = [first_of_last_month, datetime.date(year=first_of_last_month.year, month=first_of_last_month.month, day=calendar.monthrange(first_of_last_month.year, first_of_last_month.month)[1])]

        def dashed(number):
            buf = []
            for index, char in enumerate(number):
                buf.append(char)
                if index and index % 4 == 0:
                    buf.append("-")
            return "".join(buf)

        url = "https://app.cloudability.com/api/1/reporting/cost/run"
        costs = []
        for daterange in (last_month, this_month):
            log.info("Finding costs for daterange : {0}".format(daterange))
            params = {
                  "start_date": daterange[0].isoformat()
                , "end_date": daterange[1].isoformat()
                , "dimensions": "vendor_account_identifier"
                , "metrics": "unblended_cost"
                , "verbose": "1"
                , "auth_token": self.cloudability_auth
                , "max_results": 100
                , "filters": "vendor_account_identifier%3D%3D{0}".format(dashed(account)).encode('utf-8')
                }

            res = json.loads(requests.get(url, params=params).content.decode('utf-8'))
            if 'results' not in res:
                raise DashMatError("Failed to get cost from cloudability", res=res)
            costs.append(res['results'][0]['unblended_cost'])

        return costs

