from datetime import datetime, timedelta
from time import time
from flask import render_template
from .client import TornClient
from .app import app


client = TornClient()


@app.route("/")
def display_info():
    start_date = datetime.utcnow().replace(day=1)

    data = {
        "xanax_count": len(client.get_logs(log_type=2290, start_date=start_date))
    }

    return render_template(
        "basic_info.html",
        data=data
    )
