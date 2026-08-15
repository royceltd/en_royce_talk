# Copyright (c) 2026, Royce Technologies LTD and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RoyceTalkSMSCampaign(Document):
	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		balance_remaining: DF.Int
		batch_id: DF.Data | None
		customer: DF.Link | None
		customer_group: DF.Link | None
		error: DF.SmallText | None
		estimated_cost: DF.Currency
		estimated_units: DF.Int
		lead_status: DF.Literal[
			"",
			"Lead",
			"Open",
			"Replied",
			"Opportunity",
			"Quotation",
			"Lost Quotation",
			"Interested",
			"Converted",
		]
		message: DF.SmallText
		messages_failed: DF.Int
		messages_queued: DF.Int
		recipient_count: DF.Int
		scheduled_at: DF.Datetime | None
		send_to: DF.Literal["Customer", "Lead"]
		sender_id: DF.Data | None
		status: DF.Literal["Draft", "Queued", "Sending", "Completed", "Failed"]
		territory: DF.Link | None
		title: DF.Data
		total_cost: DF.Currency
		total_recipients: DF.Int
	# end: auto-generated types

	def before_submit(self):
		from royce_talk.royce_talk.bulk_send import check_submit_guardrails
		from royce_talk.royce_talk.campaign import get_recipients

		recipients = get_recipients(
			send_to=self.send_to,
			customer=self.customer,
			customer_group=self.customer_group,
			territory=self.territory,
			lead_status=self.lead_status,
		)
		cost = check_submit_guardrails(recipients, self.message)

		self.recipient_count = len(recipients)
		self.estimated_units = cost["total_units"]
		self.estimated_cost = cost["estimated_cost"]
		self.status = "Queued"

	def on_submit(self):
		frappe.enqueue(
			"royce_talk.royce_talk.campaign.send_campaign",
			queue="long",
			enqueue_after_commit=True,
			campaign_name=self.name,
		)
