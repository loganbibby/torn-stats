import json
from datetime import datetime, timedelta
from time import time
from flask import render_template, g
from .client import TornClient, LogTypes, LogCategories
from .app import app, cache
from .config import 

def compile_logs(client):
	start_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
	end_date = datetime.utcnow()
	
	request_counter = 0
	logs = []
	
	while True:
		ret_logs = client.get_logs(
			log_type=[
				LogTypes.TRAVEL, LogTypes.VAULT_WITHDRAWAL, LogTypes.VAULT_DEPOSIT, 
				LogTypes.XANAX, LogTypes.UPKEEP, LogTypes.MISSION
				
			] + LogTypes.crime_success(),
			start_date=start_date,
			end_date=end_date
		)
		
		request_counter += 1
		logs += ret_logs  # Append to the main log list
				
		if len(ret_logs) == 100:  # max results
			end_date = datetime.fromtimestamp(min([int(log["timestamp"]) for log in ret_logs])) - timedelta(seconds=1)
			continue
		
		break
		
	print(f"Retreived {len(logs)} over {request_counter} requests")
	return logs


@app.route("/")
def display_info():
	start_date = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0)
	
	profiles = []

	for api_key in app.config["TORN_API_KEYS"]:
		client = TornClient(api_key)

		logs = compile_logs(client)

		vault_logs = client.get_logs(
			[LogTypes.VAULT_DEPOSIT, LogTypes.VAULT_WITHDRAWAL],
			start_date=datetime(2022, 11, 21)
		)
		
		def get_logs(log_types):
			if not isinstance(log_types, list):
				log_types = [log_types]

			return [log for log in logs if log["log"] in log_types]
		
		profiles.append({
			"player": client.get_basic_info(),
			"xanax": len(get_logs([LogTypes.XANAX.value, LogTypes.XANAX_OD.value])),
			"crimes": len(get_logs([log_type.value for log_type in LogTypes.crime_success()])),
			"missions": len(get_logs(LogTypes.MISSION.value)),
			"travel": int(sum([l["data"]["duration"] for l in get_logs(LogTypes.TRAVEL.value)]) / 60),
			"travel_count": len(get_logs(LogTypes.TRAVEL.value)),
			"empty_blood_bag": client.get_blood(start_date=start_date),
			"money_in": client.get_money_received(start_date=start_date),
			"money_out": round(client.get_money_spent(start_date=start_date)),
			"upkeep": sum([l["data"]["upkeep_paid"] for l in get_logs(LogTypes.UPKEEP.value)]),
			"strength_energy": sum([l["data"]["energy_used"] for l in get_logs(LogTypes.GYM_STRENGTH.value)]),
			"speed_energy": sum([l["data"]["energy_used"] for l in get_logs(LogTypes.GYM_SPEED.value)]),
			"defense_energy": sum([l["data"]["energy_used"] for l in get_logs(LogTypes.GYM_DEFENSE.value)]),
			"dexterity_energy": sum([l["data"]["energy_used"] for l in get_logs(LogTypes.GYM_DEXTERITY.value)]),
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
