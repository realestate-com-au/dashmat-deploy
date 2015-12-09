from python_dashing.core_modules.amazon_base.server import ServerMixin
from python_dashing.core_modules.base import ServerBase
from python_dashing.errors import PythonDashingError

from itertools import zip_longest
from itertools import chain
import calendar
import requests
import datetime
import logging
import json

log = logging.getLogger("custom.scaling.server")

class Server(ServerBase, ServerMixin):
    def setup(self, **kwargs):
        errors = []
        for key in ("dev_account", "stg_account", "prod_account", "role_to_assume", "cloudability_auth_token"):
            if key not in kwargs:
                errors.append(MissingServerOption(wanted=key, module="custom.scaling"))
            else:
                setattr(self, key, kwargs[key])

        if errors:
            raise MissingServerOption(_errors=errors)

    @property
    def cloudability_auth(self):
        if not getattr(self, "_cloudability_auth", None):
            self._cloudability_auth = self.cloudability_auth_token
            if callable(self._cloudability_auth):
                self._cloudability_auth = self._cloudability_auth()
        return self._cloudability_auth

    @property
    def routes(self):
        yield "/scaling", self.scaling

    def scaling(self):
        dev = json.loads(self.get_string("scaling-{0}".format(self.dev_account)).decode('utf-8'))
        stg = json.loads(self.get_string("scaling-{0}".format(self.stg_account)).decode('utf-8'))
        prod = json.loads(self.get_string("scaling-{0}".format(self.prod_account)).decode('utf-8'))

        by_account = []
        applications = {}
        for name, acnt in (('dev', dev), ('stg', stg), ('prod', prod)):
            by_account.append((name, acnt))
            for options in acnt['autoscaling']:
                if options['name'] not in applications:
                    applications[options['name']] = {}
                applications[options['name']][name] = options

        def td(options):
            if not options:
                return '<td class="empty"></td>'
            kls = "green" if options['alive'] == options['desired'] else "yellow"
            kls = "red" if options['alive'] == 0 and options['desired'] > 0 else kls
            return '<td class="{0}">{1} | {2} | {3}</td>'.format(kls, options['desired'], options['alive'], options['dead'])

        applications = reversed(sorted(applications.items(), key= lambda item: 'prod' in item[1]))
        return "results.jade", {"td": td, "applications": applications, "by_account": by_account}

    @property
    def update_registration(self):
        yield "#scaling", "/scaling", {"every": 60}

    @property
    def register_checks(self):
        def named(name):
            def ret(func):
                func.__name__ = name
                return func
            return ret

        yield "*/5 * * * *", named("dev_stats")(lambda t: self.make_stats(self.dev_account))
        yield "*/5 * * * *", named("stg_stats")(lambda t: self.make_stats(self.stg_account))
        yield "*/5 * * * *", named("prod_stats")(lambda t: self.make_stats(self.prod_account))

    def make_stats(self, account):
        session = self.make_boto_session(account)
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

        log.info("Finding cost from cloudability for {0}".format(account))
        cost = self.cost_from_cloudability(account)
        self.set_string("scaling-{0}".format(account), json.dumps({"dead": total_num_dead_instances, "alive": total_num_alive_instances, "autoscaling": found, "cost": cost}))

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
                raise PythonDashingError("Failed to get cost from cloudability", res=res)
            costs.append(res['results'][0]['unblended_cost'])

        return costs

