###About
Python library for Paymill API V2.

API reference: https://www.paymill.com/sl-si/documentation-3/reference/api-reference/

No dependencies. Pretty much untested. Use at your own and your client's risk. Feedback very much welcome.

###Usage:
	from paymill import Paymill

	paymill = Paymill("your-private-key")

	# payments api method
	paymill.payments.method(params...)

	# payments api method
	paymill.preauthorizations.method(params...)

	# payments api method
	paymill.transactions.method(params...)

	# payments api method
	paymill.clients.method(params...)

	# payments api method
	paymill.refunds.method(params...)

	# payments api method
	paymill.offers.method(params...)

	# payments api method
	paymill.subscriptions.method(params...)
