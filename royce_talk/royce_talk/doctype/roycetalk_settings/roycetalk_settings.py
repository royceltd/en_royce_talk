# Copyright (c) 2026, Royce Technologies LTD and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import get_url


class RoyceTalkSettings(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		api_base_url: DF.Data
		api_key: DF.Password
		current_balance: DF.Int
		current_balance_value: DF.Currency
		default_country_code: DF.Data | None
		default_sender_id: DF.Data
		delivery_callback_url: DF.Data | None
		enabled: DF.Check
		last_balance_check: DF.Datetime | None
		low_balance_alert_sent: DF.Check
		low_balance_threshold: DF.Int
		override_core_sms: DF.Check
		test_phone_number: DF.Data | None
	# end: auto-generated types

	def validate(self):
		self.delivery_callback_url = get_url(
			"/api/method/royce_talk.royce_talk.doctype.roycetalk_sms_log.roycetalk_sms_log.delivery_webhook"
		)


@frappe.whitelist()
def send_test_sms():
	"""Called from the 'Send Test SMS' button on RoyceTalk Settings."""
	settings = frappe.get_single("RoyceTalk Settings")
	if not settings.test_phone_number:
		frappe.throw(_("Please enter a Test Phone Number first."))

	from royce_talk.royce_talk.utils import send_single_sms

	return send_single_sms(
		phone_number=settings.test_phone_number,
		text_message="This is a test message from RoyceTalk, sent via your Frappe site.",
	)
