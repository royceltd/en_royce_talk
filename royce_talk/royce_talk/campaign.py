# Copyright (c) 2026, Royce Technologies LTD and contributors
# For license information, please see license.txt

"""Recipient targeting for RoyceTalk SMS Campaign (marketing: Customer + Lead).

Two different consent defaults by design, per an explicit decision -- not an
oversight:
  - Customer: gated on `royce_talk_sms_consent` on Contact, opted OUT by default.
    A Contact is only ever included if someone explicitly checked that box.
  - Lead: gated on `royce_talk_sms_opted_out` on Lead, opted IN by default. A Lead
    is included unless someone explicitly opted them out (or their status is
    "Do Not Contact", which always excludes regardless of that field).

Employee/Supplier (operational, not marketing) live in royce_talk/operational.py
instead, with no consent gating at all -- see that module's docstring for why.
"""

import frappe

from royce_talk.royce_talk.bulk_send import estimate_cost


def get_recipients(
	send_to: str = "Customer",
	customer: str | None = None,
	customer_group: str | None = None,
	territory: str | None = None,
	lead_status: str | None = None,
) -> list[dict]:
	"""Re-run at both preview time and actual send time -- consent/status/filters may
	have changed in between."""
	if send_to == "Lead":
		return _get_lead_recipients(territory=territory, status=lead_status)
	return _get_customer_recipients(customer=customer, customer_group=customer_group, territory=territory)


def _get_customer_recipients(customer=None, customer_group=None, territory=None) -> list[dict]:
	conditions = ["con.royce_talk_sms_consent = 1", "ifnull(con.mobile_no, '') != ''"]
	values = {}

	if customer:
		conditions.append("cust.name = %(customer)s")
		values["customer"] = customer
	if customer_group:
		conditions.append("cust.customer_group = %(customer_group)s")
		values["customer_group"] = customer_group
	if territory:
		conditions.append("cust.territory = %(territory)s")
		values["territory"] = territory

	query = f"""
		select distinct con.name as name, con.mobile_no as mobile_no
		from `tabContact` con
		inner join `tabDynamic Link` dl
			on dl.parent = con.name and dl.parenttype = 'Contact' and dl.link_doctype = 'Customer'
		inner join `tabCustomer` cust on cust.name = dl.link_name
		where {" and ".join(conditions)}
	"""
	return frappe.db.sql(query, values, as_dict=True)


def _get_lead_recipients(territory=None, status=None) -> list[dict]:
	conditions = [
		"lead.royce_talk_sms_opted_out = 0",
		"ifnull(lead.status, '') != 'Do Not Contact'",
		"(ifnull(lead.mobile_no, '') != '' or ifnull(lead.phone, '') != '')",
		"lead.docstatus != 2",
	]
	values = {}

	if territory:
		conditions.append("lead.territory = %(territory)s")
		values["territory"] = territory
	if status:
		conditions.append("lead.status = %(status)s")
		values["status"] = status

	query = f"""
		select lead.name as name, ifnull(nullif(lead.mobile_no, ''), lead.phone) as mobile_no
		from `tabLead` lead
		where {" and ".join(conditions)}
	"""
	return frappe.db.sql(query, values, as_dict=True)


@frappe.whitelist()
def preview_recipients(name: str) -> dict:
	"""Called from the "Preview Recipients & Cost" button. Computes and caches the
	numbers shown on the form; does not send anything."""
	doc = frappe.get_doc("RoyceTalk SMS Campaign", name)
	doc.check_permission("write")

	recipients = get_recipients(
		send_to=doc.send_to,
		customer=doc.customer,
		customer_group=doc.customer_group,
		territory=doc.territory,
		lead_status=doc.lead_status,
	)
	cost = estimate_cost(doc.message, len(recipients))

	doc.db_set(
		{
			"recipient_count": len(recipients),
			"estimated_units": cost["total_units"],
			"estimated_cost": cost["estimated_cost"],
		},
		update_modified=False,
	)

	return {
		"recipient_count": len(recipients),
		**cost,
	}


def send_campaign(campaign_name: str):
	"""Background job (enqueued from RoyceTalk SMS Campaign.on_submit)."""
	from royce_talk.royce_talk.bulk_send import send_bulk

	def _recipients(doc):
		return get_recipients(
			send_to=doc.send_to,
			customer=doc.customer,
			customer_group=doc.customer_group,
			territory=doc.territory,
			lead_status=doc.lead_status,
		)

	send_bulk("RoyceTalk SMS Campaign", campaign_name, _recipients)
