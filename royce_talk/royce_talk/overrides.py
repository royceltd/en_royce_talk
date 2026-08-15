# Copyright (c) 2026, Royce Technologies LTD and contributors
# For license information, please see license.txt

"""Hooked in via `send_sms` in hooks.py.

Frappe's core SMS abstraction (frappe.core.doctype.sms_settings.sms_settings.send_sms)
is what powers the Notification doctype's "SMS" channel as well as OTP / 2FA messages.
When present, an app's `send_sms` hook fully replaces that function -- so this override
decides, per call, whether to route through RoyceTalk or fall back to whatever is
configured in the core "SMS Settings" doctype.
"""

import json

import frappe
from frappe import _


def send_sms_override(receiver_list, msg, sender_name="", success_msg=True):
	settings = frappe.get_single("RoyceTalk Settings")

	if isinstance(receiver_list, str):
		receiver_list = json.loads(receiver_list)
		if not isinstance(receiver_list, list):
			receiver_list = [receiver_list]

	if not settings.enabled or not settings.override_core_sms:
		_send_via_core_gateway(receiver_list, msg, success_msg)
		return

	from royce_talk.royce_talk.utils import send_single_sms

	sent_to = []
	for receiver in receiver_list:
		try:
			send_single_sms(phone_number=receiver, text_message=frappe.safe_decode(msg))
			sent_to.append(receiver)
		except Exception:
			# Numbers not in international (+countrycode) format will fail normalization
			# here -- see RoyceTalk SMS Log / Error Log for the specific recipient/reason.
			frappe.log_error(
				title=_("RoyceTalk: failed to send SMS to {0}").format(receiver),
				message=frappe.get_traceback(),
			)

	if sent_to and success_msg:
		frappe.msgprint(_("SMS sent successfully"))


def _send_via_core_gateway(receiver_list, msg, success_msg):
	"""Replicates frappe.core.doctype.sms_settings.sms_settings.send_sms's default
	behaviour, called directly (not via frappe.get_hooks) to avoid re-entering this
	same override."""
	from frappe.core.doctype.sms_settings.sms_settings import send_via_gateway, validate_receiver_nos

	receiver_list = validate_receiver_nos(receiver_list)
	arg = {
		"receiver_list": receiver_list,
		"message": frappe.safe_decode(msg).encode("utf-8"),
		"success_msg": success_msg,
	}

	if frappe.db.get_single_value("SMS Settings", "sms_gateway_url"):
		send_via_gateway(arg)
	else:
		frappe.msgprint(_("Please Update SMS Settings"))
