# Copyright (c) 2026, Royce Technologies LTD and contributors
# For license information, please see license.txt

import frappe
from frappe import _

from royce_talk.royce_talk.utils import RoyceTalkError, check_balance


def check_balance_and_alert():
	"""Hourly scheduled task (see hooks.py). Refreshes the cached RoyceTalk balance
	and emails System Managers once when it drops below the configured threshold --
	not on every tick, and it un-arms itself once the balance recovers (e.g. after a
	top-up) so a future drop alerts again."""
	settings = frappe.get_single("RoyceTalk Settings")
	if not settings.enabled or not settings.get_password("api_key", raise_exception=False):
		return

	try:
		data = check_balance()
	except RoyceTalkError:
		frappe.log_error(
			title=_("RoyceTalk balance check failed"),
			message=frappe.get_traceback(),
		)
		return

	threshold = settings.low_balance_threshold or 0
	current_balance = data.get("current_balance") or 0

	if threshold and current_balance < threshold:
		if not settings.low_balance_alert_sent:
			_send_low_balance_alert(current_balance, data.get("balance_value"), data.get("currency"))
			frappe.db.set_value("RoyceTalk Settings", "RoyceTalk Settings", "low_balance_alert_sent", 1)
	elif settings.low_balance_alert_sent:
		frappe.db.set_value("RoyceTalk Settings", "RoyceTalk Settings", "low_balance_alert_sent", 0)


def _send_low_balance_alert(current_balance, balance_value, currency):
	from frappe.utils.user import get_system_managers

	recipients = get_system_managers(only_name=True)
	if not recipients:
		return

	subject = _("RoyceTalk SMS balance is low ({0} units)").format(current_balance)
	message = _(
		"Your RoyceTalk SMS balance has dropped to {0} units (~{1} {2}). SMS sends -- "
		"including any Notifications routed through RoyceTalk -- will start failing once "
		"the balance runs out. Top up at https://roycetalk.com/dashboard, or review "
		"RoyceTalk Settings on your site."
	).format(current_balance, balance_value, currency or "")

	try:
		frappe.sendmail(recipients=recipients, subject=subject, message=message)
	except Exception:
		frappe.log_error(
			title=_("Failed to send RoyceTalk low balance alert email"),
			message=frappe.get_traceback(),
		)
