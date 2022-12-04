from enum import IntEnum
import requests


class LogTypes(IntEnum):
    XANAX = 2290
    MISSION = 7815
    CRIME = 5725


class TornClient(object):
    url = "https://api.torn.com"

    def __init__(self, api_key):
        self.api_key = api_key

    def execute(self, endpoint, selection, **kwargs):
        url = f"{self.url}/{endpoint}/"

        query_params = {
            "selections": selection,
            "key": self.api_key
        }
        query_params.update(**kwargs)

        r = requests.get(url, params=query_params)

        print(f"URL: {url} - {query_params}")

        return r.json()

    def get_basic_info(self):
        return self.execute(
            "user", "basic"
        )

    def get_logs(self, log_type=None, start_date=None, end_date=None, **kwargs):
        if start_date:
            kwargs["from"] = int(round(start_date.timestamp()))

        if end_date:
            kwargs["to"] = int(round(end_date.timestamp()))

        if log_type:
            kwargs["log"] = int(log_type)

        payload = self.execute(
            "user", "log",
            **kwargs
        )["log"]

        if not payload:
            return []

        return [v for k, v in payload.items()]
