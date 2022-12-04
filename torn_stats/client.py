import requests
from .app import app


class TornClient(object):
    url = "https://api.torn.com"

    def execute(self, endpoint, selection, **kwargs):
        url = f"{self.url}/{endpoint}/"

        query_params = {
            "selections": selection,
            "key": app.config["TORN_API_KEY"]
        }
        query_params.update(**kwargs)

        r = requests.get(url, params=query_params)

        return r.json()

    def get_logs(self, log_type=None, start_date=None, end_date=None, **kwargs):
        if start_date:
            kwargs["from"] = int(round(start_date.timestamp()))

        if end_date:
            kwargs["to"] = int(round(end_date.timestamp()))

        if log_type:
            kwargs["log"] = log_type

        payload = self.execute(
            "user", "log",
            **kwargs
        )["log"]

        if not payload:
            return []

        return [v for k, v in payload.items()]
