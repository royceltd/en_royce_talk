# Copyright (c) 2026, Royce Technologies LTD and contributors
# For license information, please see license.txt

"""ADR-023 in royce_ip: the invoice Notification is created once, and a client who
turns it on keeps it on through every migrate."""

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils.fixtures import sync_fixtures

from royce_talk.bulk_sms.install import INVOICE_NOTIFICATION, create_invoice_notification


class TestInvoiceNotification(IntegrationTestCase):
	def tearDown(self):
		frappe.db.rollback()

	def test_created_disabled_when_missing(self):
		frappe.delete_doc("Notification", INVOICE_NOTIFICATION, force=True, ignore_missing=True)
		self.assertTrue(create_invoice_notification())
		self.assertEqual(frappe.db.get_value("Notification", INVOICE_NOTIFICATION, "enabled"), 0)

	def test_a_client_who_enabled_it_keeps_it_enabled(self):
		create_invoice_notification()
		frappe.db.set_value("Notification", INVOICE_NOTIFICATION, "enabled", 1)
		self.assertFalse(create_invoice_notification())
		sync_fixtures("royce_talk")
		self.assertEqual(frappe.db.get_value("Notification", INVOICE_NOTIFICATION, "enabled"), 1)
