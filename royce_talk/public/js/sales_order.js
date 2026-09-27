// "SMS > Notify Customer" on submitted Sales Orders.
// Shipped as app code via doctype_js (it was a Client Script record until
// v16.2.0; patches/v16_2/remove_shipped_client_scripts.py removes that copy).

frappe.ui.form.on("Sales Order", {
	refresh(frm) {
		if (frm.doc.docstatus !== 1) {
			return;
		}
		frm.add_custom_button(
			__("Notify Customer"),
			() => royce_talk_order_notify_dialog(frm),
			__("SMS")
		);
	},
});

function royce_talk_order_notify_dialog(frm) {
	const default_message = __(
		"Dear {0}, your order {1} for {2} has been confirmed. Thank you for your business.",
		[
			frm.doc.customer_name || frm.doc.customer,
			frm.doc.name,
			format_currency(frm.doc.grand_total, frm.doc.currency),
		]
	);

	const dialog = new frappe.ui.Dialog({
		title: __("Notify Customer via SMS"),
		fields: [
			{
				fieldname: "phone_number",
				fieldtype: "Data",
				label: __("Phone Number"),
				default: frm.doc.contact_mobile,
				description: __("Local (0712345678) or international (+254712345678) format accepted."),
				reqd: 1,
			},
			{
				fieldname: "text_message",
				fieldtype: "Small Text",
				label: __("Message"),
				default: default_message,
				reqd: 1,
			},
		],
		primary_action_label: __("Send"),
		primary_action(values) {
			frappe.call({
				method: "royce_talk.bulk_sms.utils.send_single_sms",
				args: {
					phone_number: values.phone_number,
					text_message: values.text_message,
					reference_doctype: frm.doc.doctype,
					reference_name: frm.doc.name,
				},
				freeze: true,
				freeze_message: __("Sending SMS..."),
				callback(r) {
					dialog.hide();
					if (r.message) {
						frappe.show_alert({
							message: __("SMS sent (message id: {0})", [r.message.message_id]),
							indicator: "green",
						});
					}
				},
			});
		},
	});

	dialog.show();
}
