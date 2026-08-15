# Copyright (c) 2026, Royce Technologies LTD and contributors
# For license information, please see license.txt

"""Recipient targeting for RoyceTalk Operational Broadcast (Employee + Supplier).

Deliberately no consent gating here, unlike royce_talk/campaign.py's Customer/Lead
targeting: these are internal/operational audiences (employment and vendor
relationships), not marketing to the public, so RoyceTalk SMS Campaign's
consent-field logic doesn't apply and shouldn't be reused here. Keep this doctype and
campaign.py's separate for that reason -- don't merge them later without re-thinking
what that would mean for Employees/Suppliers.
"""

import frappe

from royce_talk.royce_talk.bulk_send import estimate_cost


def get_recipients(
	send_to: str = "Employee",
	company: str | None = None,
	department: str | None = None,
	branch: str | None = None,
	employee_status: str | None = "Active",
	supplier: str | None = None,
	supplier_group: str | None = None,
) -> list[dict]:
	if send_to == "Supplier":
		return _get_supplier_recipients(supplier=supplier, supplier_group=supplier_group)
	return _get_employee_recipients(
		company=company, department=department, branch=branch, status=employee_status
	)


def _get_employee_recipients(company=None, department=None, branch=None, status="Active") -> list[dict]:
	conditions = ["ifnull(emp.cell_number, '') != ''", "emp.docstatus != 2"]
	values = {}

	if status:
		conditions.append("emp.status = %(status)s")
		values["status"] = status
	if company:
		conditions.append("emp.company = %(company)s")
		values["company"] = company
	if department:
		conditions.append("emp.department = %(department)s")
		values["department"] = department
	if branch:
		conditions.append("emp.branch = %(branch)s")
		values["branch"] = branch

	query = f"""
		select emp.name as name, emp.cell_number as mobile_no
		from `tabEmployee` emp
		where {" and ".join(conditions)}
	"""
	return frappe.db.sql(query, values, as_dict=True)


def _get_supplier_recipients(supplier=None, supplier_group=None) -> list[dict]:
	conditions = ["ifnull(con.mobile_no, '') != ''"]
	values = {}

	if supplier:
		conditions.append("sup.name = %(supplier)s")
		values["supplier"] = supplier
	if supplier_group:
		conditions.append("sup.supplier_group = %(supplier_group)s")
		values["supplier_group"] = supplier_group

	query = f"""
		select distinct con.name as name, con.mobile_no as mobile_no
		from `tabContact` con
		inner join `tabDynamic Link` dl
			on dl.parent = con.name and dl.parenttype = 'Contact' and dl.link_doctype = 'Supplier'
		inner join `tabSupplier` sup on sup.name = dl.link_name
		where {" and ".join(conditions)}
	"""
	return frappe.db.sql(query, values, as_dict=True)


@frappe.whitelist()
def preview_recipients(name: str) -> dict:
	"""Called from the "Preview Recipients & Cost" button. Computes and caches the
	numbers shown on the form; does not send anything."""
	doc = frappe.get_doc("RoyceTalk Operational Broadcast", name)
	doc.check_permission("write")

	recipients = get_recipients(
		send_to=doc.send_to,
		company=doc.company,
		department=doc.department,
		branch=doc.branch,
		employee_status=doc.employee_status,
		supplier=doc.supplier,
		supplier_group=doc.supplier_group,
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


def send_broadcast(broadcast_name: str):
	"""Background job (enqueued from RoyceTalk Operational Broadcast.on_submit)."""
	from royce_talk.royce_talk.bulk_send import send_bulk

	def _recipients(doc):
		return get_recipients(
			send_to=doc.send_to,
			company=doc.company,
			department=doc.department,
			branch=doc.branch,
			employee_status=doc.employee_status,
			supplier=doc.supplier,
			supplier_group=doc.supplier_group,
		)

	send_bulk("RoyceTalk Operational Broadcast", broadcast_name, _recipients)
