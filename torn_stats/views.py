from datetime import datetime, timedelta
from time import time
from flask import render_template, g
from .client import TornClient, LogTypes
from .app import app, cache


@app.route("/")
@cache.cached(timeout=30)
def display_info():
    start_date = datetime.utcnow().replace(day=1)

    profiles = []

    for api_key in app.config["TORN_API_KEYS"]:
        client = TornClient(api_key)

        profiles.append({
            "player": client.get_basic_info(),
            "data": {
                "Xanax Taken": len(client.get_logs(LogTypes.XANAX, start_date=start_date)),
                "Crimes Committed": len(client.get_logs(LogTypes.CRIME, start_date=start_date)),
                "Missions Completed": len(client.get_logs(LogTypes.MISSION, start_date=start_date)),
            }
        })

    return render_template(
        "basic_info.html",
        start_date=start_date,
        profiles=profiles
    )
