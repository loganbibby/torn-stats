from datetime import datetime, timedelta
from time import time
from flask import render_template
from .client import TornClient, LogTypes
from .app import app


client = TornClient()


@app.route("/")
def display_info():
    start_date = datetime.utcnow().replace(day=1)

    data = {
        "xanax_count": len(client.get_logs(LogTypes.XANAX, start_date=start_date)),
        "crime_count": len(client.get_logs(LogTypes.CRIME, start_date=start_date)),
        "mission_count": len(client.get_logs(LogTypes.MISSION, start_date=start_date)),
    }

    return render_template(
        "basic_info.html",
        basic_info=client.get_basic_info(),
        start_date=start_date,
        data=data
    )
