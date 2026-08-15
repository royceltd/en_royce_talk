# Copyright (c) 2026, Royce Technologies LTD and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RoyceTalkOperationalBroadcast(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		balance_remaining: DF.Int
		batch_id: DF.Data | None
		branch: DF.Link | None
		company: DF.Link | None
		department: DF.Link | None
		employee_status: DF.Literal["Active", "Inactive", "Suspended", "Left"]
		error: DF.SmallText | None
		estimated_cost: DF.Currency
		estimated_units: DF.Int
		message: DF.SmallText
		messages_failed: DF.Int
		messages_queued: DF.Int
		recipient_count: DF.Int
		scheduled_at: DF.Datetime | None
		send_to: DF.Literal["Employee", "Supplier"]
		sender_id: DF.Data | None
		status: DF.Literal["Draft", "Queued", "Sending", "Completed", "Failed"]
		supplier: DF.Link | None
		supplier_group: DF.Link | None
		title: DF.Data
		total_cost: DF.Currency
		total_recipients: DF.Int
	# end: auto-generated types

	def before_submit(self):
		from royce_talk.royce_talk.bulk_send import check_submit_guardrails
		from royce_talk.royce_talk.operational import get_recipients

		recipients = get_recipients(
			send_to=self.send_to,
			company=self.company,
			department=self.department,
			branch=self.branch,
			employee_status=self.employee_status,
			supplier=self.supplier,
			supplier_group=self.supplier_group,
		)
		cost = check_submit_guardrails(recipients, self.message)

		self.recipient_count = len(recipients)
		self.estimated_units = cost["total_units"]
		self.estimated_cost = cost["estimated_cost"]
		self.status = "Queued"

	def on_submit(self):
		frappe.enqueue(
			"royce_talk.royce_talk.operational.send_broadcast",
			queue="long",
			enqueue_after_commit=True,
			broadcast_name=self.name,
		)
