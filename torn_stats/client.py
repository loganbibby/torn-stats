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
    CRIME = 5725
    CRIMES = 5720


class LogCategories(IntEnum):
    MONEY_INCOMING = 17
    MONEY_OUTGOING = 14
    CRIME = 136


class TornClient(object):
	url = "https://api.torn.com"
	use_cache = True

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
			
			if "to" in query_params and query_params["to"] > int(datetime.now().replace(hour=0, minute=0, second=0).timestamp()):
				timeout = 60 * 60
			else:
				timeout = 60 * 60 * 24 * 7
			
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

		payload = self.execute(
			"user", "log",
			**kwargs
		)["log"]

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
			for key in ["money", "money_mugged", "pay", "cost","total_cost"]:
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
			for key in ["money", "money_mugged", "cost", "total_cost", "upkeep_paid", "value", "bet"]:
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