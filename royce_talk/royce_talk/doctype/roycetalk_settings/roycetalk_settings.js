// Copyright (c) 2026, Royce Technologies LTD and contributors
// For license information, please see license.txt

frappe.ui.form.on("RoyceTalk Settings", {
	refresh(frm) {
		frm.set_df_property("delivery_callback_url", "read_only", 1);
	},

	check_balance_now(frm) {
		if (frm.is_dirty()) {
			frappe.msgprint(__("Please save your changes before checking the balance."));
			return;
		}

		frappe.call({
			method: "royce_talk.royce_talk.utils.check_balance",
			freeze: true,
			freeze_message: __("Checking balance..."),
			callback(r) {
				if (r.message) {
					frappe.show_alert({
						message: __("Balance: {0} units (~{1} {2})", [
							r.message.current_balance,
							r.message.balance_value,
							r.message.currency,
						]),
						indicator: "green",
					});
					frm.reload_doc();
				}
			},
		});
	},

	send_test_sms(frm) {
		if (frm.is_dirty()) {
			frappe.msgprint(__("Please save your changes before sending a test SMS."));
			return;
		}
		if (!frm.doc.test_phone_number) {
			frappe.msgprint(__("Please enter a Test Phone Number first."));
			return;
		}

		frappe.call({
			method: "royce_talk.royce_talk.doctype.roycetalk_settings.roycetalk_settings.send_test_sms",
			freeze: true,
			freeze_message: __("Sending test SMS..."),
			callback(r) {
				if (r.message) {
					frappe.show_alert({
						message: __("Test SMS sent (message id: {0})", [r.message.message_id]),
						indicator: "green",
					});
				}
			},
		});
	},
});
