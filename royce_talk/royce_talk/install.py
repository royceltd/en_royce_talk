# Copyright (c) 2026, Royce Technologies LTD and contributors
# For license information, please see license.txt

import frappe


def after_install():
	# Populate the Delivery Callback URL shown on RoyceTalk Settings so it's ready
	# to copy into the RoyceTalk dashboard without requiring a manual save first.
	settings = frappe.get_single("RoyceTalk Settings")
	settings.flags.ignore_mandatory = True
	settings.save(ignore_permissions=True)
