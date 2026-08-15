# Copyright (c) 2026, Royce Technologies LTD and contributors
# For license information, please see license.txt

"""Shared submit-guardrail and background-send logic for RoyceTalk's bulk-send
doctypes (RoyceTalk SMS Campaign, RoyceTalk Operational Broadcast). Each doctype owns
its own recipient targeting/consent rules and calls into this module for the parts
that are identical: cost estimation, the configured/non-empty/balance checks that
block submit, and the actual chunked bulk API call plus result write-back.
"""

import frappe
from frappe import _
from frappe.utils import flt

from royce_talk.royce_talk.utils import RoyceTalkError, check_balance, estimate_units


def estimate_cost(message: str, recipient_count: int) -> dict:
	"""Local cost estimate using RoyceTalk's documented per-unit pricing and whatever
	rate we last saw from a balance check -- avoids a live API round-trip just to show
	a preview number. Falls back to KES 0.50/unit if we've never checked the balance."""
	settings = frappe.get_single("RoyceTalk Settings")
	rate = 0.5
	if settings.current_balance:
		rate = flt(settings.current_balance_value) / settings.current_balance or 0.5

	units = estimate_units(message)
	return {
		"units_per_recipient": units,
		"total_units": units * recipient_count,
		"estimated_cost": units * recipient_count * rate,
	}


def check_submit_guardrails(recipients: list, message: str) -> dict:
	"""Shared submit-time checks: RoyceTalk configured, at least one recipient, and
	estimated cost within the current (live-checked) RoyceTalk balance. Throws on
	failure; returns the cost estimate dict on success. Deliberately does not know
	anything about consent -- that's each caller's own responsibility before it gets
	here (RoyceTalk SMS Campaign's recipient queries are consent-gated; RoyceTalk
	Operational Broadcast's are not, by design, since it targets Employees/Suppliers)."""
	settings = frappe.get_single("RoyceTalk Settings")
	if not settings.enabled or not settings.get_password("api_key", raise_exception=False):
		frappe.throw(_("RoyceTalk is not configured. Set it up in RoyceTalk Settings first."))

	if not recipients:
		frappe.throw(_("No recipients match these filters. Nothing to send."))

	cost = estimate_cost(message, len(recipients))

	try:
		balance_data = check_balance()
	except RoyceTalkError as e:
		frappe.throw(_("Could not verify RoyceTalk balance before sending: {0}").format(e))

	if flt(balance_data.get("balance_value")) < cost["estimated_cost"]:
		frappe.throw(
			_(
				"Estimated cost (~{0} KES for {1} recipients) exceeds your RoyceTalk balance "
				"({2} KES). Top up before sending, or narrow the recipient filters."
			).format(cost["estimated_cost"], len(recipients), balance_data.get("balance_value"))
		)

	return cost


def send_bulk(doctype: str, docname: str, get_recipients_fn):
	"""Generic background sender (called via frappe.enqueue from each doctype's
	on_submit). Re-resolves recipients fresh via get_recipients_fn(doc) -- consent or
	filters may have changed since submit -- sends via RoyceTalk's bulk endpoint, and
	writes the aggregate result back onto the document."""
	doc = frappe.get_doc(doctype, docname)
	if doc.docstatus != 1:
		return

	doc.db_set("status", "Sending", update_modified=False)

	settings = frappe.get_single("RoyceTalk Settings")
	recipients = get_recipients_fn(doc)

	from royce_talk.royce_talk.utils import _normalize_phone

	phone_numbers = []
	for r in recipients:
		try:
			phone_numbers.append(_normalize_phone(r["mobile_no"], settings.default_country_code))
		except Exception:
			# Un-normalizable number on file -- RoyceTalk would reject it anyway;
			# skip rather than fail the whole send over one bad record.
			continue

	if not phone_numbers:
		doc.db_set(
			{"status": "Failed", "error": _("No recipients with a usable phone number.")},
			update_modified=False,
		)
		return

	from royce_talk.royce_talk.utils import send_bulk_sms

	result = send_bulk_sms(
		phone_numbers=phone_numbers,
		text_message=doc.message,
		sender_id=doc.sender_id or settings.default_sender_id,
		settings=settings,
		callback_url=settings.delivery_callback_url,
		client_ref=doc.name,
		scheduled_at=str(doc.scheduled_at) if doc.scheduled_at else None,
	)

	doc.db_set(
		{
			"batch_id": ", ".join(result["batch_ids"]),
			"total_recipients": result["total_recipients"] or len(phone_numbers),
			"messages_queued": result["messages_queued"],
			"messages_failed": result["messages_failed"],
			"total_cost": result["total_cost"],
			"balance_remaining": result["balance_remaining"],
			"error": "; ".join(result["errors"]),
			"status": "Completed" if result["messages_queued"] else "Failed",
		},
		update_modified=False,
	)
