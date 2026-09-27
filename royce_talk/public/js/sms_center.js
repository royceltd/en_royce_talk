// Points SMS Center users at consent-gated Bulk SMS Campaigns.
// Shipped as app code via doctype_js (it was a Client Script record until
// v16.2.0; patches/v16_2/remove_shipped_client_scripts.py removes that copy).

frappe.ui.form.on("SMS Center", {
	refresh(frm) {
		frappe.call({
			method: "royce_talk.bulk_sms.utils.is_site_wide_gateway_active",
			callback(r) {
				if (r.message) {
					frm.set_intro(
						__(
							"Bulk SMS is your site-wide SMS gateway, and this tool sends to everyone " +
							"matching your filter with no consent check. For customer/marketing SMS, use " +
							"<a href=\"/app/bulk-sms-campaign/new\">Bulk SMS Campaign</a> instead " +
							"-- it only sends to Contacts with SMS Marketing Consent."
						),
						"orange",
						true
					);
					frm.set_df_property("send_sms", "hidden", 1);
				}
			},
		});
	},
});
