// Copyright (c) 2026, Royce Technologies LTD and contributors
// For license information, please see license.txt

frappe.ui.form.on("RoyceTalk Operational Broadcast", {
	refresh(frm) {
		if (frm.doc.docstatus === 0 && !frm.is_new()) {
			frm.add_custom_button(__("Refresh Preview"), () => preview(frm));
		}
	},

	preview_recipients(frm) {
		preview(frm);
	},
});

function preview(frm) {
	if (!frm.doc.message) {
		frappe.msgprint(__("Enter a message first."));
		return;
	}
	if (frm.is_dirty()) {
		frappe.msgprint(__("Please save your changes before previewing."));
		return;
	}

	frappe.call({
		method: "royce_talk.royce_talk.operational.preview_recipients",
		args: { name: frm.doc.name },
		freeze: true,
		freeze_message: __("Checking recipients..."),
		callback(r) {
			if (!r.message) {
				return;
			}
			const d = r.message;
			frm.reload_doc();
			frappe.msgprint({
				title: __("Broadcast Preview"),
				indicator: d.recipient_count ? "blue" : "orange",
				message: __(
					"<b>{0}</b> recipients match these filters.<br>Estimated: <b>{1}</b> SMS units, ~<b>{2}</b> KES.",
					[d.recipient_count, d.total_units, d.estimated_cost]
				),
			});
		},
	});
}
