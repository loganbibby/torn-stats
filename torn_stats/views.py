import json
from datetime import datetime, timedelta
from time import time
from flask import render_template, g
from .client import TornClient, LogTypes
from .app import app, cache


@app.route("/")
@cache.cached(timeout=30)
def display_info():
    #start_date = datetime(2022, 11, 21)
    start_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
    end_date = datetime.utcnow().replace(hour=23, minute=59, second=59)

    profiles = []

    for api_key in app.config["TORN_API_KEYS"]:
        client = TornClient(api_key)

        logs = []

        date = start_date

        while True:
            if date > end_date:
                 break

            logs += client.get_logs([
                    LogTypes.TRAVEL, LogTypes.VAULT_WITHDRAWAL, LogTypes.VAULT_DEPOSIT,
                    LogTypes.XANAX, LogTypes.MISSION, LogTypes.UPKEEP, LogTypes.CRIME, #LogTypes.CRIMES,
                ],
                start_date=date,
                end_date=date.replace(hour=23, minute=59, second=59)
            )

            date += timedelta(days=1)

        vault_logs = client.get_logs(
            [LogTypes.VAULT_DEPOSIT, LogTypes.VAULT_WITHDRAWAL],
            start_date=datetime(2022, 11, 21)
        )

        print(f"Log count: {len(logs)}")

        def get_logs(log_types):
            if not isinstance(log_types, list):
                log_types = [log_types]

            return [log for log in logs if log["log"] in log_types]

        profiles.append({
            "player": client.get_basic_info(),
            "xanax": len(get_logs([LogTypes.XANAX.value, LogTypes.XANAX_OD.value])),
            #"crimes": len([t ["data"]["crime"] for t in get_logs(LogTypes.CRIME.value)]),#(LogCategories.CRIME.value)]),
            "crimes": len(get_logs(LogTypes.CRIME.value)),
            #"crimes": len(["data"]["crime"]client.get_crime(start_date=start_date)) / 60,
            "missions": len(get_logs(LogTypes.MISSION.value)),
            "travel": int(sum([l["data"]["duration"] for l in get_logs(LogTypes.TRAVEL.value)]) / 60),
            "travel_count": len(get_logs(LogTypes.TRAVEL.value)),
            "money_in": client.get_money_received(start_date=start_date),
            "money_out": client.get_money_spent(start_date=start_date),
            "upkeep": sum([l["data"]["upkeep_paid"] for l in get_logs(LogTypes.UPKEEP.value)]),
            "vault": sum([
                sum([l["data"]["deposited"] for l in vault_logs if "deposited" in l["data"] and l["data"]["property"] == 13]),
                sum([l["data"]["withdrawn"] for l in vault_logs if "withdrawn" in l["data"] and l["data"]["property"] == 13]) * -1,
            ]),
        })

    return render_template(
        "basic_info.html",
        start_date=start_date,
        profiles=profiles
    )
