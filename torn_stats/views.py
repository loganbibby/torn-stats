from datetime import datetime, timedelta
from time import time
from flask import render_template, g
from .client import TornClient, LogTypes
from .app import app, cache


@app.route("/")
#@cache.cached(timeout=30)
def display_info():
    start_date = datetime.utcnow().replace(day=1)

    profiles = []

    for api_key in app.config["TORN_API_KEYS"]:
        client = TornClient(api_key)

        logs = client.get_logs([
                LogTypes.TRAVEL, LogTypes.VAULT_WITHDRAWAL, LogTypes.VAULT_DEPOSIT,
                LogTypes.XANAX, LogTypes.CRIME, LogTypes.MISSION
            ], start_date=start_date
        )

        def get_logs(log_type):
            return [log for log in logs if log["log"] == log_type]

        profiles.append({
            "player": client.get_basic_info(),
            "xanax": len(get_logs(LogTypes.XANAX.value)),
            "crimes": len(get_logs(LogTypes.CRIME.value)),
            "missions": len(get_logs(LogTypes.MISSION.value)),
            "travel": int(sum([l["data"]["duration"] for l in get_logs(LogTypes.TRAVEL.value)]) / 60),
            "money_in": client.get_money_received(start_date=start_date),
            "money_out": client.get_money_spent(start_date=start_date),
            "vault": sum([
                sum([l["data"]["deposited"] for l in get_logs(LogTypes.VAULT_DEPOSIT.value)]),
                sum([l["data"]["withdrawn"] for l in get_logs(LogTypes.VAULT_WITHDRAWAL.value)]) * -1,
            ]),
        })

    return render_template(
        "basic_info.html",
        start_date=start_date,
        profiles=profiles
    )
