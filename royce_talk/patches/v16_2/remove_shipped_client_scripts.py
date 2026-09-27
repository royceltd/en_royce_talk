# Copyright (c) 2026, Royce Technologies LTD and contributors
# For license information, please see license.txt

"""Until v16.2.0 the Bulk SMS form scripts shipped as Client Script records (a
fixture), re-imported on every migrate. They are app code now (public/js/ via
doctype_js, and the Bulk SMS Settings form script), so the records would run the
same code twice. Removed only if still exactly what we shipped: a client who
edited one keeps their copy (ADR-023: nothing a client changed is overwritten)."""

import hashlib

import frappe

SHIPPED = {
	"Bulk SMS - Sales Invoice Notify Customer": "12f3d1c83f1ee991a885b7a3e77335cdc5d5021ccbd243d1874fd56cadba96e0",
	"Bulk SMS - Sales Order Notify Customer": "d6014e3e3f68d2addfb2aa1666506a20ababf87a0ad81bfaeeb69876078ce71f",
	"Bulk SMS - SMS Center Consent Warning": "370e27ce220a1e1b025377f0830664f07b7db7a882f682f7d279c9fab2866b78",
	"Bulk SMS - Settings Activation Notice": "2b2d04281b0d8f3883e130092f265bb6f7408de89d862bdfe3c5a5166eb0d1a8",
}


def execute():
	remove_if_unchanged(SHIPPED)


def remove_if_unchanged(shipped: dict) -> list:
	removed = []
	for name, sha256 in shipped.items():
		script = frappe.db.get_value("Client Script", name, "script")
		if script is None:
			continue
		if hashlib.sha256(script.replace("\r\n", "\n").encode()).hexdigest() != sha256:
			continue
		frappe.delete_doc("Client Script", name, ignore_permissions=True, force=True)
		removed.append(name)
	return removed
