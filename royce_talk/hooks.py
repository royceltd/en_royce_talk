app_name = "royce_talk"
app_title = "Royce Talk"
app_publisher = "Royce Technologies LTD"
app_description = "Send SMS notifications to customers via the Royce Talk SMS API"
app_email = "josphatkips@gmail.com"
app_license = "mit"

# Apps
# ------------------

# RoyceTalk SMS Campaign / Operational Broadcast query ERPNext's Customer, Lead,
# Employee, and Supplier tables directly -- this app doesn't function without ERPNext
# installed, so bench should refuse to install it standalone rather than fail later
# with a confusing "table doesn't exist" error the first time someone opens a campaign.
required_apps = ["erpnext"]

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "royce_talk",
# 		"logo": "/assets/royce_talk/logo.png",
# 		"title": "Royce Talk",
# 		"route": "/royce_talk",
# 		"has_permission": "royce_talk.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/royce_talk/css/royce_talk.css"
# app_include_js = "/assets/royce_talk/js/royce_talk.js"

# include js, css files in header of web template
# web_include_css = "/assets/royce_talk/css/royce_talk.css"
# web_include_js = "/assets/royce_talk/js/royce_talk.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "royce_talk/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "royce_talk/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# automatically load and sync documents of this doctype from downstream apps
# importable_doctypes = [doctype_1]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "royce_talk.utils.jinja_methods",
# 	"filters": "royce_talk.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "royce_talk.install.before_install"
after_install = "royce_talk.royce_talk.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "royce_talk.uninstall.before_uninstall"
# after_uninstall = "royce_talk.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "royce_talk.utils.before_app_install"
# after_app_install = "royce_talk.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "royce_talk.utils.before_app_uninstall"
# after_app_uninstall = "royce_talk.utils.after_app_uninstall"

# Build
# ------------------
# To hook into the build process

# after_build = "royce_talk.build.after_build"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "royce_talk.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

scheduler_events = {
	"hourly": [
		"royce_talk.royce_talk.tasks.check_balance_and_alert",
	],
}

# Testing
# -------

# before_tests = "royce_talk.install.before_tests"

# Extend DocType Class
# ------------------------------
#
# Specify custom mixins to extend the standard doctype controller.
# extend_doctype_class = {
# 	"Task": "royce_talk.custom.task.CustomTaskMixin"
# }

# Overriding Methods
# ------------------------------

# Route Frappe's core SMS sending (Notification "SMS" channel, OTP, 2FA) through
# RoyceTalk when "Use as Site-wide SMS Gateway" is enabled in RoyceTalk Settings.
# See royce_talk/royce_talk/overrides.py for the fallback behaviour when it's off.
send_sms = "royce_talk.royce_talk.overrides.send_sms_override"

# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "royce_talk.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "royce_talk.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["royce_talk.utils.before_request"]
# after_request = ["royce_talk.utils.after_request"]

# Job Events
# ----------
# before_job = ["royce_talk.utils.before_job"]
# after_job = ["royce_talk.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"royce_talk.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

# Fixtures
# --------
# Ships "Notify Customer" buttons on Sales Invoice/Sales Order (as Client Scripts, so
# they work without a JS build step), a ready-to-enable Notification template for
# SMS-on-submit, and the Contact-level SMS Marketing Consent field the campaign
# feature gates on.
fixtures = [
	{"doctype": "Client Script", "filters": [["module", "=", "Royce Talk"]]},
	{"doctype": "Notification", "filters": [["name", "=", "RoyceTalk - Sales Invoice Submitted (SMS)"]]},
	{"doctype": "Custom Field", "filters": [["fieldname", "like", "royce_talk_%"]]},
]

