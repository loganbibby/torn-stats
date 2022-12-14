from enum import IntEnum
from datetime import datetime
import hashlib
import requests
from .app import cache


class LogTypes(IntEnum):
	XANAX = 2290
	XANAX_OD = 2291
	MISSION = 7815
	TRAVEL = 6000
	GYM_DEFENSE = 5301
	GYM_STRENGTH = 5300
	GYM_DEXTERITY = 5303
	GYM_SPEED = 5302
	ATTACK_MUG = 8155
	ATTACK_HOSPITALIZE = 8160
	ATTACK_LEAVE = 8150
	VAULT_DEPOSIT = 5850
	VAULT_WITHDRAWAL = 5851
	TRAVEL_BUY = 4201
	COMPANY_PAY = 6221
	COMPANY_TRAIN = 6264
	MARKET_SELL = 1104
	BAZAAR_SELL = 1221
	UPKEEP = 5920
	CRIME_SUCCESS_POINT = 5730
	CRIME_SUCCESS_MONEY = 5720
	CRIME_SUCCESS_TOKEN = 5735
	CRIME_SUCCESS_ITEM = 5725
	EMPTY_BLOOD_BAG = 2340
	
	@classmethod
	def crime_success(cls):
		return [
			cls.CRIME_SUCCESS_ITEM, cls.CRIME_SUCCESS_MONEY,
			cls.CRIME_SUCCESS_POINT, cls.CRIME_SUCCESS_TOKEN
		]


class LogCategories(IntEnum):
	MONEY_INCOMING = 17
	MONEY_OUTGOING = 14
	CRIME = 136  # This pulls ~all~ crime included failures


class TornClient(object):
	url = "https://api.torn.com"
	use_cache = False

	def __init__(self, api_key):
		self.api_key = api_key

	def execute(self, endpoint, selection, **kwargs):
		url = f"{self.url}/{endpoint}/"

		query_params = {
			"selections": selection,
			"key": self.api_key
		}
		query_params.update(**kwargs)
		
		cache_key = self.get_cache_key(
			url=url,
			params=query_params
		)
		
		payload = cache.get(cache_key)
		
		if not payload or not self.use_cache:
			r = requests.get(url, params=query_params)
			payload = r.json()
			print(r.status_code)
			print(r.url)
			
			if "to" in query_params and query_params["to"] > int(datetime.utcnow().replace(hour=0, minute=0, second=0).timestamp()):
				timeout = 60 * 60
			else:
				timeout = 0
			
			cache.set(cache_key, payload, timeout=timeout)

		return payload
	
	def get_cache_key(self, **kwargs):
		parts = [f"{str(key)}_{str(value)}" for key, value in kwargs.items()]
		hash = hashlib.md5("__".join(parts).encode()).hexdigest()
		return f"request_{self.api_key}_{hash}"

	def get_basic_info(self):
		return self.execute(
			"user", "basic"
		)

	def get_logs(self, log_type=None, log_category=None, start_date=None, end_date=None, **kwargs):
		if start_date:
			kwargs["from"] = int(round(start_date.timestamp()))

		if end_date:
			kwargs["to"] = int(round(end_date.timestamp()))

		if log_type:
			if isinstance(log_type, list):
				kwargs["log"] = ",".join([str(t.value) for t in log_type])
			else:
				kwargs["log"] = int(log_type)

		if log_category:
			if isinstance(log_category, list):
				kwargs["cat"] = ",".join([str(t.value) for t in log_category])
			else:
				kwargs["cat"] = int(log_category)
		
		print(kwargs)

		payload = self.execute(
			"user", "log",
			**kwargs
		).get("log")

		if not payload:
			return []

		return [v for k, v in payload.items()]

	def get_total_travel_time(self, start_date=None, end_date=None):
		logs = self.get_logs(
			LogTypes.TRAVEL,
			start_date=start_date,
			end_date=end_date
		)

		return round(sum([l["data"]["duration"] for l in logs]) / 60, 0)

	def get_money_received(self, **kwargs):
		logs = self.get_logs(
			log_category=LogCategories.MONEY_INCOMING,
			**kwargs
		)

		money = 0

		for log in logs:
			for key in ["money", "money_mugged", "pay", "cost","total_cost","money_given","worth","received","won_amount","money_gained","amount","bounty_reward","total_value"]:
				if key not in log["data"]:
					continue
				money += log["data"][key]

		return money

	def get_money_spent(self, **kwargs):
		logs = self.get_logs(
			log_category=LogCategories.MONEY_OUTGOING,
			**kwargs
		)

		money = 0

		for log in logs:
			for key in ["money", "money_mugged", "cost", "total_cost", "upkeep_paid", "value", "bet","worth","bet_amount","returned"]:
				if key not in log["data"]:
					continue
				money += log["data"][key]

		return money

	def get_vault_deposits(self, **kwargs):
		logs = self.get_logs(
			LogTypes.VAULT_DEPOSIT,
			**kwargs
		)

		return sum([l["data"]["deposited"] for l in logs])

	def get_blood(self, **kwargs):
		logs = self.get_logs(
			LogTypes.EMPTY_BLOOD_BAG,
			**kwargs
		)

		return len([l["data"]["faction"] for l in logs if "faction" in l["data"] and l["data"]["faction"] != 0]) 

	def get_vault_withdrawals(self, **kwargs):
		logs = self.get_logs(
			LogTypes.VAULT_WITHDRAWAL,
			**kwargs
		)

		return sum([l["data"]["withdrawn"] for l in logs])

	def get_vault_net(self, **kwargs):
		return self.get_vault_deposits(**kwargs) - self.get_vault_withdrawals(**kwargs)

	# def get_upkeep(self, **kwargs):
	#    logs = self.get_logs(
	 #       LogTypes.upkeep,
	  #      **kwargs
	   # return upkeep_paid(**kwargs)
	   # )
		
	def get_upkeep(self, **kwargs):
		logs = self.get_logs(
			log_category=LogCategories.MONEY_OUTGOING,
			**kwargs
		)

		money = 0

		for log in logs:
			for key in ["upkeep_paid"]:
				if key not in log["data"]:
					continue
				money += log["data"][key]

		return money
		
	def get_crime(self, **kwargs):
		logs = self.get_logs(
			log_category=LogCategories.CRIME,
			**kwargs
		)

		crime = 0

		for log in logs:
			for key in ["crime"]:
				if key not in log["data"]:
					continue
				crime += log["data"][key]

		return crime