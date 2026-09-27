# Copyright (c) 2026, Royce Technologies LTD and contributors
# For license information, please see license.txt

import frappe

INVOICE_NOTIFICATION = "Bulk SMS - Sales Invoice Submitted"


def after_install():
	# Populate the Delivery Callback URL shown on Bulk SMS Settings so it's ready
	# to copy into the RoyceTalk dashboard without requiring a manual save first.
	settings = frappe.get_single("Bulk SMS Settings")
	settings.flags.ignore_mandatory = True
	settings.save(ignore_permissions=True)

	create_invoice_notification()


def create_invoice_notification() -> bool:
	"""A ready-to-enable "SMS the customer when an invoice is submitted" Notification,
	created disabled and only if it doesn't exist. Install-time, not a fixture: until
	v16.2.0 it was a fixture, so every migrate switched it back off on a client who
	had turned it on (ADR-023: once created, it's the client's)."""
	if frappe.db.exists("Notification", INVOICE_NOTIFICATION):
		return False
	frappe.get_doc(
		{
			"doctype": "Notification",
			"name": INVOICE_NOTIFICATION,
			"subject": "Sales Invoice Submitted",
			"document_type": "Sales Invoice",
			"event": "Submit",
			"channel": "SMS",
			"enabled": 0,
			"is_standard": 0,
			"message": (
				"<p>Dear {{ doc.customer_name or doc.customer }},</p>\n"
				"<p>Your invoice {{ doc.name }} for {{ frappe.utils.fmt_money(doc.grand_total, currency=doc.currency) }}"
				" has been generated.</p>\n<p>Thank you for your business.</p>"
			),
			"message_type": "Markdown",
			"recipients": [{"receiver_by_document_field": "contact_mobile"}],
		}
	).insert(ignore_permissions=True, set_name=INVOICE_NOTIFICATION)
	return True
