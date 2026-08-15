# Copyright (c) 2026, Royce Technologies LTD and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RoyceTalkSMSLog(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		balance_after: DF.Currency
		client_ref: DF.Data | None
		cost: DF.Currency
		error: DF.SmallText | None
		message: DF.SmallText | None
		message_id: DF.Data | None
		recipient: DF.Data
		reference_doctype: DF.Link | None
		reference_name: DF.DynamicLink | None
		sender_id: DF.Data | None
		sms_units: DF.Int
		status: DF.Literal["Pending", "Sent", "Delivered", "Failed"]
	# end: auto-generated types
	pass


@frappe.whitelist(allow_guest=True)
def delivery_webhook():
	"""Receives delivery status callbacks from RoyceTalk (configured as callback_url
	when sending, and shown on RoyceTalk Settings for manual setup on their dashboard).

	NOTE: RoyceTalk's docs do not (yet) describe a signature/HMAC scheme for verifying
	that a callback genuinely originated from them. Until they provide one, treat this
	endpoint as informational only -- it updates status on a best-effort basis matched
	by message_id, and never trust it for anything security-sensitive.
	"""
	payload = frappe.request.get_json(silent=True) or frappe.local.form_dict

	message_id = payload.get("message_id") or payload.get("data", {}).get("message_id")
	status = payload.get("status") or payload.get("data", {}).get("status")

	if not message_id:
		frappe.local.response.http_status_code = 400
		return {"success": False, "error": "message_id is required"}

	log_name = frappe.db.get_value("RoyceTalk SMS Log", {"message_id": message_id})
	if not log_name:
		frappe.local.response.http_status_code = 404
		return {"success": False, "error": "Unknown message_id"}

	status_map = {
		"delivered": "Delivered",
		"sent": "Sent",
		"failed": "Failed",
		"pending": "Pending",
	}
	new_status = status_map.get((status or "").lower())
	if new_status:
		frappe.db.set_value("RoyceTalk SMS Log", log_name, "status", new_status)

	return {"success": True}
