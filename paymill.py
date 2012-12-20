# -*- coding: utf-8 -*-
"""
"""
import base64
import urllib
import urllib2
import json

class Paymill():
	PRIVATE_KEY = None
	API_URL = "https://api.paymill.de/v2/"
	HEADERS = {}
	DEF_CURRENCY = "EUR"

	__lazy__ = {
		"payments": lambda o: Payments(o),
		"preauthorizations": lambda o: Preauthorizations(o),
		"transactions": lambda o: Transactions(o),
		"clients": lambda o: Clients(o),
		"refunds": lambda o: Refunds(o),
		"offers": lambda o: Offers(o),
		"subscriptions": lambda o: Subscriptions(o),
	}

	def __init__(self, private_key=None):
		"""
		Paymill init method
		it only sets private_key in certain scenarios
		private_key can also be hardcoded as class attribute
		"""
		if self.PRIVATE_KEY is None:
			self.PRIVATE_KEY = private_key
		if self.PRIVATE_KEY is None: raise ValueError("PRIVATE_KEY should be set")

	def __str__(self):
		return self.repr()

	def __unicode__(self):
		return self.repr()

	def str(self):
		return self.repr()

	def repr(self):
		return u"%s" % ("<PayMill: private_key='%s'>" % (self.PRIVATE_KEY,)
		)

	def __getattr__(self, item):
		"""
		lazily instantiates attributes defined in __lazy__ object
		"""
		if item in self.__lazy__:
			setattr(self, item, self.__lazy__[item](self))
			return getattr(self, item)
		raise AttributeError(item)

	def client(self, method, id="", params=None):
		"""
		handles connection to server

		id: string, unique  identifier for this endpoint entity
		params: dict, extra parameters to be passed as GET query string

		returns response object which is later manipulated some more
		"""
		if params:
			params = "?%s" % urllib.urlencode(params)
		url = "%s%s/%s/%s" % (self.API_URL, method, id, params or "")
		request = urllib2.Request(url, headers=self.HEADERS)
		base64string = base64.encodestring("%s:%s" % (self.PRIVATE_KEY, "")).replace("\n", "")
		request.add_header("Authorization", "Basic %s" % base64string)
		return  request

	def delete(self, method, id):
		"""
		DELETE http request
		"""
		request = self.client(method, id)
		request.get_method = lambda: "DELETE"
		return self._response(request)

	def get(self, method, id="", params=None):
		"""
		GET http request
		"""
		if params and not isinstance(params, (dict,)): raise ValueError("params should be of type dict")

		request = self.client(method, id, params)
		return self._response(request)

	def put(self, method, data, id=""):
		"""
		PUT http request
		"""
		request = self.client(method, id)
		request.get_method = lambda: "PUT"
		request.add_data(urllib.urlencode(data))
		return self._response(request)

	def post(self, method, data, id=""):
		"""
		POST http request
		"""
		if not isinstance(method, (str,)): raise ValueError("method should be of type string")
		if data is None: raise ValueError("data should not be None for post requests")
		if not isinstance(data, (dict,)): raise ValueError("data should be of type dict")

		data = dict((key, val)for key, val in data.iteritems() if val is not None)
		request = self.client(method, id)
		request.add_data(urllib.urlencode(data))
		return self._response(request)

	def _response(self, request):
		"""
		reads response from server
		handles responses and errors

		returns json as python dict object
		"""
		response, result = None, None
		try:
			response = urllib2.urlopen(request)
			result = response.read()
		except urllib2.HTTPError, e:
			if e.code == 401:
				raise ApiError(ApiError.ERR_UNAUTHORIZED)
			elif e.code == 403:
				raise ApiError(ApiError.ERR_PRECONDITION_FAILED)
			elif e.code == 404:
				raise ApiError(ApiError.ERR_NOT_FOUND)
			elif e.code == 412:
				raise ApiError(ApiError.ERR_PRECONDITION_FAILED)
			elif e.code >= 500:
				raise ApiError(ApiError.ERR_SERVER_ERROR)
			else:
				raise e
		finally:
			if result:
				response.close()
		return json.loads(result)


class ApiError(Exception):
	"""
	api errors with customised error messages, ...
	"""
	ERR_UNAUTHORIZED = (401, "Unauthorized", "Jim, You have to provide your private API Key.")
	ERR_TRANSACTION_ERROR = (403, "Transaction Error", "Transaction could not be completed, please check your payment data.")
	ERR_NOT_FOUND = (404, "Not Found", "There is no entity with this identifier, did you use the right one?")
	ERR_PRECONDITION_FAILED = (412, "Precondition Failed", "I guess you're missing at least one required parameter?")
	ERR_SERVER_ERROR = (5, "Server Error", "Doh, we did something wrong :/")

	def __init__(self, signature, **kwargs):
		self.code, self.msg, self.description = signature
		self.params = kwargs

	def __str__(self):
		return self.repr()

	def __unicode__(self):
		return self.repr()

	def str(self):
		return self.repr()

	def repr(self):
		return u"%s" % ("<ApiError: %s - %s - %s%s>" %
						(self.code, self.msg, self.description, self.params if self.params else "")
		)


class Endpoint(object):
	"""
	super class for endpoint classes
	"""

	def __init__(self, paymill):
		self._paymill = paymill

	def __str__(self):
		return self.repr()

	def __unicode__(self):
		return self.repr()

	def str(self):
		return self.repr()

	def repr(self):
		return u"%s" % ("%s" % (type(self),))


class Payments(Endpoint):
	"""
	payments endpoint class
	"""
	method = "payments"

	def create(self, token, client=None):
		"""
		payments endpoint create method

		token: string, unique  credit card token
		client: string, unique  client identifier

		returns python dict object
		"""
		if token is None: raise ValueError("token should not be None")
		if client and not isinstance(client, (str,)): raise ValueError("client should be of type string")

		data = {
			"token": token,
			"client": client
		}
		return self._paymill.post(self.method, data)

	def details(self, id):
		"""
		payments endpoint details method

		id: string, unique  identifier for this payment

		returns python dict object
		"""
		if id is None: raise ValueError("id should not be None")
		if not isinstance(id, (str,)): raise ValueError("id should be of type string")

		return self._paymill.get(self.method, id)

	def remove(self, id):
		"""
		payments endpoint remove method

		id: string, unique  identifier for this payment

		returns python dict object
		"""
		if id is None: raise ValueError("id should not be None")
		if not isinstance(id, (str,)): raise ValueError("id should be of type string")

		return self._paymill.delete(self.method, id)

	def list(self, order=None):
		"""
		payment endpoint list method

		order: string, options count|offset|created_at

		returns python dict object
		"""
		if order and not isinstance(order, (str,)): raise ValueError("order should not be of type string")
		if order and order not in ["count", "offset", "created_at"]:
			raise ValueError("order should be either of count|offset|created_at")

		if order:
			params = {"order": order}
			return self._paymill.get(self.method, params=params)
		return self._paymill.get(self.method)


class Preauthorizations(Endpoint):
	"""
	preauthorizations endpoint class
	"""
	method = "preauthorizations"

	def create(self, amount, currency=Paymill.DEF_CURRENCY, token=None, payment=None):
		"""
		preauthorizations create method

		amount: integer, (in cents) which will be charged
		currency: string, ISO 4217 formatted currency code
		token: string, the identifier of a token -  either token or payment
		payment: string, the identifier of a payment (only creditcard-object) -  either token or payment

		returns python dict object
		"""
		if amount is None: raise ValueError("amount should not be None")
		if not isinstance(amount, (int,)): raise ValueError("amount should be of type integer")
		if currency is None: raise ValueError("currency should not be None")
		if isinstance(currency, (str,)): raise ValueError("currency should be of type string")
		if token and not isinstance(token, (str,)): raise ValueError("token should be of type string")
		if payment and not isinstance(payment, (str,)): raise ValueError("payment should be of type string")
		if not token and not payment: raise ValueError("at least token or payment has to be passed")

		data = {
			"amount": amount,
			"currency": currency,
			"token": token,
			"payment": payment,
		}
		return self._paymill.post(self.method, data)

	def details(self, id):
		"""
		preauthorizations endpoint details method

		id: string, unique  identifier for this preauthorization

		returns python dict object
		"""
		if id is None: raise ValueError("id should not be None")
		if not isinstance(id, (str,)): raise ValueError("id should be of type string")

		return self._paymill.get(self.method, id)

	def list(self, order=None):
		"""
		preauthorizations endpoint list method

		order: string, options count|offset|created_at

		returns python dict object
		"""
		if order and not isinstance(order, (str,)): raise ValueError("order should not be of type string")
		if order and order not in ["count", "offset", "created_at"]:
			raise ValueError("order should be either of count|offset|created_at")

		if order:
			params = {"order": order}
			return self._paymill.get(self.method, params=params)
		return self._paymill.get(self.method)


class Transactions(Endpoint):
	"""
	transactions endpoint class
	"""
	method = "transactions"

	def create(self, amount, currency=Paymill.DEF_CURRENCY, description=None, client=None, token=None, payment=None, preauthorization=None):
		"""
		transactions endpoint create method

		amount: integer, (in cents) which will be charged
		currency: string, ISO 4217 formatted currency code, default EUR
		description: string, description for this transaction
		client: string, the identifier of a client
		token: string, the identifier of a token -  if token, payment and preauthorization must be None
		payment: string, the identifier of the payment -  if payment, token and preauthorization must be None
		preauthorization : string, the identifier of the preauthorization  -  if preauthorization , token and payment must be None

		returns python dict object
		"""
		if amount is None: raise ValueError("amount should not be None")
		if not isinstance(amount, (int,)): raise ValueError("amount should be of type integer")
		if currency is None: raise ValueError("currency should not be None")
		if not isinstance(currency, (str,)): raise ValueError("currency should be of type string")
		if client and not isinstance(client, (str,)): raise ValueError("client should be of type string")
		if token is None: raise ValueError("token should not be None")
		if not isinstance(token, (str,)): raise ValueError("token should be of type string")

		if payment and not isinstance(payment, (str,)): raise ValueError("payment should be of type string")
		if preauthorization and not isinstance(preauthorization, (str,)): raise ValueError("preauthorization should be of type string")

		if client and not payment: raise ValueError("client is passed, payment should be as well")
		if token and payment or\
		   payment and preauthorization or\
		   token and preauthorization:
			raise ValueError("only either of token|payment|preauthorization is acceptable, not all")

		data = {
			"amount": amount,
			"currency": currency,
			"description": description,
			"client": client,
			"token": token,
			"payment": payment,
			"preauthorization": preauthorization,
		}
		return self._paymill.post(self.method, data)

	def details(self, id):
		"""
		transactions endpoint details method

		id: string, unique  identifier for this transaction

		returns python dict object
		"""
		if id is None: raise ValueError("id should not be None")
		if not isinstance(id, (str,)): raise ValueError("id should be of type string")

		return self._paymill.get(self.method, id)

	def list(self, order=None):
		"""
		transactions endpoint list method

		order: string, options count|offset|created_at

		returns python dict object
		"""
		if order and not isinstance(order, (str,)): raise ValueError("order should not be of type string")
		if order and order not in ["count", "offset", "created_at"]:
			raise ValueError("order should be either of count|offset|created_at")

		if order:
			params = {"order": order}
			return self._paymill.get(self.method, params=params)
		return self._paymill.get(self.method)


class Refunds(Endpoint):
	"""
	refunds endpoint class
	"""
	method = "refunds"

	def transaction(self, id, amount, description=None):
		"""
		refunds endpoint transaction method

		amount: integer (in cents) which will be charged
		description: string, additional description for this refund

		returns python dict object
		"""
		if id is None: raise ValueError("id should not be None")
		if not isinstance(id, (str,)): raise ValueError("id should be of type string")
		if amount is None: raise ValueError("amount should not be None")
		if not isinstance(amount, (int,)): raise ValueError("amount should be of type integer")

		data = {
			"amount": amount,
			"description": description,
		}
		return self._paymill.post(self.method, data, id)

	def details(self, id):
		"""
		refunds endpoint details method

		id: string, unique  identifier for this refund

		returns python dict object
		"""
		if id is None: raise ValueError("id should not be None")
		if not isinstance(id, (str,)): raise ValueError("id should be of type string")

		return self._paymill.get(self.method, id)

	def list(self, order=None):
		"""
		refunds endpoint list method

		order: string, options count|offset|transaction|client|amount|created_at

		returns python dict object
		"""
		if order and not isinstance(order, (str,)): raise ValueError("order should not be of type string")
		if order and order not in ["count", "offset", "transaction", "client", "amount", "created_at"]:
			raise ValueError("order should be either of count|offset|transaction|client|amount|created_at")

		if order:
			params = {"order": order}
			return self._paymill.get(self.method, params=params)
		return self._paymill.get(self.method)


class Clients(Endpoint):
	"""
	clients endpoint class
	"""
	method = "clients"

	def create(self, email, description=None):
		"""
		clients endpoint create method

		email: string, mail address of the client
		description: string or null, additional description for this client

		returns python dict object
		"""
		if email is None: raise ValueError("email should not be None")
		if not isinstance(email, (str,)): raise ValueError("email should be of type string")

		data = {
			"email": email,
			"description": description,
		}
		return self._paymill.post(self.method, data)

	def details(self, id):
		"""
		clients endpoint details method

		id: string, unique  identifier for this client

		returns python dict object
		"""
		if id is None: raise ValueError("id should not be None")
		if not isinstance(id, (str,)): raise ValueError("id should be of type string")

		return self._paymill.get(self.method, id)

	def update(self, id, email, description=None):
		"""
		clients endpoint update method

		email: string, mail address of the client
		description: string or null, additional description for this client

		returns python dict object
		"""
		if id is None: raise ValueError("id should not be None")
		if not isinstance(id, (str,)): raise ValueError("id should be of type string")
		if email is None: raise ValueError("email should not be None")
		if not isinstance(email, (str,)): raise ValueError("email should be of type string")

		data = {
			"email": email,
			"description": description,
		}
		return self._paymill.put(self.method, data, id)

	def remove(self, id):
		"""
		clients endpoint remove method

		id: string, unique  identifier for this client

		returns python dict object
		"""
		if id is None: raise ValueError("id should not be None")
		if not isinstance(id, (str,)): raise ValueError("id should be of type string")

		return self._paymill.delete(self.method, id)

	def list(self, order=None):
		"""
		clients endpoint list method

		order: string, options count|offset|creditcard|email|created_at

		returns python dict object
		"""
		if order and not isinstance(order, (str,)): raise ValueError("order should not be of type string")
		if order and order not in ["count", "offset", "creditcard", "email", "created_at"]:
			raise ValueError("order should be either of count|offset|creditcard|email|created_at")

		if order:
			params = {"order": order}
			return self._paymill.get(self.method, params=params)
		return self._paymill.get(self.method)

	def export(self):
		"""
		"""
		pass


class Offers(Endpoint):
	"""
	offers endpoint class
	"""
	method = "offers"

	def create(self, amount, interval, name, currency=Paymill.DEF_CURRENCY):
		"""
		offers endpoint create method

		amount: integer, (in cents) which will be charged
		interval: string, either of week|month|year, defining how often the client should be charged.
		name: string, name for this offer
		currency: string, ISO 4217 formatted currency code, default EUR

		returns python dict object
		"""
		if amount is None: raise ValueError("amount should not be None")
		if not isinstance(amount, (int,)): raise ValueError("amount should be of type integer")
		if currency is None: raise ValueError("currency should not be None")
		if not isinstance(currency, (str,)): raise ValueError("currency should be of type string")
		if interval is None: raise ValueError("interval should not be None")
		if interval not in ["week", "month", "year"]: raise ValueError("interval enum should be either of week|month|year")
		if name is None: raise ValueError("name should not be None")
		if not isinstance(name, (str,)): raise ValueError("name should be of type string")

		data = {
			"amount": amount,
			"currency": currency,
			"interval": interval,
			"name": name,
		}
		return self._paymill.post(self.method, data)

	def details(self, id):
		"""
		offers endpoint details method

		id: string, unique  identifier for this offer

		returns python dict object
		"""
		if id is None: raise ValueError("id should not be None")
		if not isinstance(id, (str,)): raise ValueError("id should be of type string")

		return self._paymill.get(self.method, id)

	def update(self, id, name):
		"""
		offers endpoint update method

		id: string, unique  identifier for this offer
		name: string, name for this offer

		returns python dict object
		"""
		if id is None: raise ValueError("id should not be None")
		if not isinstance(id, (str,)): raise ValueError("id should be of type string")
		if name is None: raise ValueError("name should not be None")
		if not isinstance(name, (str,)): raise ValueError("name should be of type string")

		data = {
			"name": name,
		}
		return self._paymill.put(self.method, data, id)

	def remove(self, id):
		"""
		offers endpoint remove method

		id: string, unique   identifier for this offer

		returns python dict object
		"""
		if id is None: raise ValueError("id should not be None")
		if not isinstance(id, (str,)): raise ValueError("id should be of type string")

		return self._paymill.delete(self.method, id)

	def list(self, order=None):
		"""
		offers endpoint list method

		order: string, options count|offset|interval|amount|created_at|trial_period_days

		returns python dict object
		"""
		if order and not isinstance(order, (str,)): raise ValueError("order should not be of type string")
		if order and order not in ["count", "offset", "interval", "amount", "created_at", "trial_period_days"]:
			raise ValueError("order should be either of count|offset|interval|amount|created_at|trial_period_days")

		if order:
			params = {"order": order}
			return self._paymill.get(self.method, params=params)
		return self._paymill.get(self.method)


class Subscriptions(Endpoint):
	"""
	subscriptions endpoint class
	"""
	method = "subscriptions"

	def create(self, client, offer, payment):
		"""
		subscriptions endpoint create method

		client: string, the identifier of a client
		offer: string, unique offer identifier
		payment: string, unique payment identifier

		returns python dict object
		"""
		if client is None: raise ValueError("client should not be None")
		if not isinstance(client, (str,)): raise ValueError("client should be of type string")
		if offer is None: raise ValueError("offer should not be None")
		if not isinstance(offer, (str,)): raise ValueError("offer should be of type string")
		if payment is None: raise ValueError("payment should not be None")
		if not isinstance(payment, (str,)): raise ValueError("payment should be of type string")

		data = {
			"client": client,
			"offer": offer,
			"payment": payment,
		}
		return self._paymill.post(self.method, data)

	def details(self, id):
		"""
		subscriptions endpoint details method

		id: string, unique identifier for this subscription

		returns python dict object
		"""
		if id is None: raise ValueError("id should not be None")
		if not isinstance(id, (str,)): raise ValueError("id should be of type string")

		return self._paymill.get(self.method, id)

	def update(self, id, cancel_at_period_end):
		"""
		subscriptions endpoint update method

		cancel_at_period_end: boolean, cancel this subscription immediately or at the end of the current period?

		returns python dict object
		"""
		if id is None: raise ValueError("id should not be None")
		if not isinstance(id, (str,)): raise ValueError("id should be of type string")
		if cancel_at_period_end is None: raise ValueError("cancel_at_period_end should not be None")
		if not isinstance(cancel_at_period_end, (bool, int)): raise ValueError("cancel_at_period_end should be type bool")

		data = {
			"cancel_at_period_end": bool(cancel_at_period_end),
		}
		return self._paymill.put(self.method, data, id)

	def remove(self, id):
		"""
		subscriptions endpoint remove method

		id: string, unique  identifier for this subscription

		returns python dict object
		"""
		if id is None: raise ValueError("id should not be None")
		if not isinstance(id, (str,)): raise ValueError("id should be of type string")

		return self._paymill.delete(self.method, id)

	def list(self, order=None):
		"""
		subscriptions endpoint list method

		order: string, options count|offset|offer|canceled_at|created_at

		returns python dict object
		"""
		if order and not isinstance(order, (str,)): raise ValueError("order should not be of type string")
		if order and order not in ["count", "offset", "offer", "canceled_at", "created_at"]:
			raise ValueError("order should be either of count|offset|offer|canceled_at|created_at")

		if order:
			params = {"order": order}
			return self._paymill.get(self.method, params=params)
		return self._paymill.get(self.method)
