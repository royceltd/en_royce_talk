# Copyright (c) 2026, Royce Technologies LTD and contributors
# For license information, please see license.txt

import math
import re
import time

import frappe
import requests
from frappe import _
from frappe.utils import cint, flt, now_datetime

SEND_ENDPOINT = "/api/v1/sms-api/send/"
BULK_SEND_ENDPOINT = "/api/v1/sms-api/send-bulk/"
BALANCE_ENDPOINT = "/api/v1/sms-api/balance/"
MAX_ATTEMPTS = 2  # 1 retry on 429 (rate limit), per RoyceTalk docs
BULK_CHUNK_SIZE = 1000  # within RoyceTalk's recommended 1,000-5,000 per request
PHONE_RE = re.compile(r"\+\d{9,15}")


class RoyceTalkError(frappe.ValidationError):
	pass


def get_settings():
	settings = frappe.get_single("RoyceTalk Settings")
	if not settings.enabled:
		frappe.throw(_("RoyceTalk integration is disabled. Enable it in RoyceTalk Settings."), RoyceTalkError)
	if not settings.get_password("api_key", raise_exception=False):
		frappe.throw(_("Please set an API Key in RoyceTalk Settings."), RoyceTalkError)
	return settings


@frappe.whitelist()
def send_single_sms(
	phone_number: str,
	text_message: str,
	sender_id: str | None = None,
	reference_doctype: str | None = None,
	reference_name: str | None = None,
	client_ref: str | None = None,
	scheduled_at: str | None = None,
) -> dict:
	"""Send a single SMS via the RoyceTalk API and log the result.

	Safe to call directly for interactive/synchronous use (e.g. a "Notify Customer"
	button on a document). For sends triggered from document events where the save
	shouldn't be blocked on an outbound HTTP call, use `queue_sms` instead.
	"""
	settings = get_settings()
	phone_number = _normalize_phone(phone_number, settings.default_country_code)
	sender_id = sender_id or settings.default_sender_id

	payload = {
		"phone_number": phone_number,
		"text_message": text_message,
		"sender_id": sender_id,
	}
	if settings.delivery_callback_url:
		payload["callback_url"] = settings.delivery_callback_url
	if client_ref:
		payload["client_ref"] = client_ref
	if scheduled_at:
		payload["scheduled_at"] = scheduled_at

	log = frappe.new_doc("RoyceTalk SMS Log")
	log.recipient = phone_number
	log.sender_id = sender_id
	log.message = text_message
	log.client_ref = client_ref
	log.reference_doctype = reference_doctype
	log.reference_name = reference_name
	log.status = "Pending"

	url = settings.api_base_url.rstrip("/") + SEND_ENDPOINT
	headers = _auth_headers(settings)
	response, body = _post_with_retry(url, payload, headers)

	if response is None:
		log.status = "Failed"
		log.error = body["error"]
	elif response.status_code == 200 and body.get("success"):
		data = body.get("data", {})
		log.status = "Sent"
		log.message_id = data.get("message_id")
		log.sms_units = cint(data.get("sms_units"))
		log.cost = data.get("cost")
		log.balance_after = data.get("balance_after")
	else:
		log.status = "Failed"
		log.error = _error_message(response, body)

	log.flags.ignore_permissions = True
	log.insert()

	if log.status == "Failed":
		frappe.throw(log.error, RoyceTalkError)

	return {
		"message_id": log.message_id,
		"status": log.status,
		"sms_units": log.sms_units,
		"cost": log.cost,
		"balance_after": log.balance_after,
	}


@frappe.whitelist()
def check_balance() -> dict:
	"""Fetch current RoyceTalk account balance and cache it on RoyceTalk Settings
	(current_balance / current_balance_value / last_balance_check), so the settings
	form always shows a recent figure without a live API call on every page load."""
	settings = get_settings()
	url = settings.api_base_url.rstrip("/") + BALANCE_ENDPOINT

	try:
		response = requests.get(url, headers=_auth_headers(settings), timeout=15)
	except requests.exceptions.RequestException as e:
		frappe.throw(_("Could not reach RoyceTalk: {0}").format(e), RoyceTalkError)

	body = _safe_json(response)
	if response.status_code != 200 or not body.get("success"):
		frappe.throw(_error_message(response, body), RoyceTalkError)

	data = body.get("data", {})
	frappe.db.set_value(
		"RoyceTalk Settings",
		"RoyceTalk Settings",
		{
			"current_balance": cint(data.get("current_balance")),
			"current_balance_value": data.get("balance_value"),
			"last_balance_check": now_datetime(),
		},
	)

	return data


@frappe.whitelist()
def is_site_wide_gateway_active() -> bool:
	"""Used by the SMS Center warning banner (see fixtures/client_script.json) to know
	whether RoyceTalk is currently the transport for frappe.core's generic send_sms --
	which SMS Center's un-gated bulk send also goes through."""
	settings = frappe.get_single("RoyceTalk Settings")
	return bool(settings.enabled and settings.override_core_sms)


def queue_sms(**kwargs):
	"""Queue an SMS send as a background job so the caller (e.g. a document's
	on_submit) isn't blocked on the outbound HTTP call. Failures are recorded in
	RoyceTalk SMS Log, not raised back to the caller."""
	frappe.enqueue(
		"royce_talk.royce_talk.utils.send_single_sms",
		queue="short",
		enqueue_after_commit=True,
		**kwargs,
	)


def send_bulk_sms(
	phone_numbers: list[str],
	text_message: str,
	sender_id: str,
	settings,
	callback_url: str | None = None,
	client_ref: str | None = None,
	scheduled_at: str | None = None,
) -> dict:
	"""Send to many recipients via RoyceTalk's native bulk endpoint (not a loop over
	send_single_sms), chunked at BULK_CHUNK_SIZE. Not whitelisted -- called from the
	SMS Campaign background job, which owns permission checks and per-campaign logging.
	Returns an aggregate dict; per-chunk failures are collected in "errors" rather than
	raised, so one bad chunk doesn't abort the rest of a large campaign."""
	url = settings.api_base_url.rstrip("/") + BULK_SEND_ENDPOINT
	headers = _auth_headers(settings)

	aggregate = {
		"batch_ids": [],
		"total_recipients": 0,
		"messages_queued": 0,
		"messages_failed": 0,
		"total_cost": 0.0,
		"balance_remaining": None,
		"errors": [],
	}

	for chunk in _chunks(phone_numbers, BULK_CHUNK_SIZE):
		payload = {
			"phone_number": chunk,
			"text_message": text_message,
			"sender_id": sender_id,
		}
		if callback_url:
			payload["callback_url"] = callback_url
		if client_ref:
			payload["client_ref"] = client_ref
		if scheduled_at:
			payload["scheduled_at"] = scheduled_at

		response, body = _post_with_retry(url, payload, headers)

		if response is None:
			aggregate["errors"].append(body["error"])
			aggregate["messages_failed"] += len(chunk)
			continue

		if response.status_code == 200 and body.get("success"):
			data = body.get("data", {})
			if data.get("batch_id"):
				aggregate["batch_ids"].append(data["batch_id"])
			aggregate["total_recipients"] += cint(data.get("total_recipients")) or len(chunk)
			aggregate["messages_queued"] += cint(data.get("messages_queued"))
			aggregate["messages_failed"] += cint(data.get("messages_failed"))
			aggregate["total_cost"] += flt(data.get("total_cost"))
			if data.get("balance_remaining") is not None:
				aggregate["balance_remaining"] = data.get("balance_remaining")
		else:
			aggregate["errors"].append(_error_message(response, body))
			aggregate["messages_failed"] += len(chunk)

	return aggregate


def estimate_units(text_message: str) -> int:
	"""RoyceTalk's documented pricing: 1-160 chars = 1 unit, 161-306 = 2 units,
	307+ = ceil(length / 153)."""
	length = len(text_message or "")
	if length <= 160:
		return 1
	if length <= 306:
		return 2
	return math.ceil(length / 153)


def _chunks(items: list, size: int):
	for i in range(0, len(items), size):
		yield items[i : i + size]


def _auth_headers(settings) -> dict:
	return {
		"Authorization": f"Bearer {settings.get_password('api_key')}",
		"Content-Type": "application/json",
	}


def _post_with_retry(url, payload, headers):
	for attempt in range(1, MAX_ATTEMPTS + 1):
		try:
			response = requests.post(url, json=payload, headers=headers, timeout=15)
		except requests.exceptions.RequestException as e:
			return None, {"error": _("Could not reach RoyceTalk: {0}").format(e)}

		if response.status_code != 429 or attempt == MAX_ATTEMPTS:
			return response, _safe_json(response)

		wait = cint(response.headers.get("Retry-After")) or 2
		time.sleep(wait)

	return response, _safe_json(response)  # pragma: no cover - unreachable, loop always returns


def _normalize_phone(phone_number: str, default_country_code: str | None = "254") -> str:
	"""Accepts +254712345678, 254712345678, or the local 0712345678 form (or whatever
	Default Country Code is set to in RoyceTalk Settings) and normalizes to E.164.
	Numbers already in another country's +format are passed through untouched."""
	country_code = (default_country_code or "254").lstrip("+")
	cleaned = re.sub(r"[\s\-()]", "", (phone_number or "").strip())

	if not cleaned:
		frappe.throw(_("Phone number is required"), RoyceTalkError)

	if cleaned.startswith("+"):
		normalized = cleaned
	elif cleaned.startswith("00"):  # international dialing prefix, e.g. 00254712345678
		normalized = "+" + cleaned[2:]
	elif cleaned.startswith(country_code):
		normalized = "+" + cleaned
	elif cleaned.startswith("0"):
		normalized = f"+{country_code}{cleaned[1:]}"
	else:
		frappe.throw(
			_(
				"'{0}' doesn't look like a valid phone number. Use international format "
				"(+254712345678), the {1} prefix ({1}712345678), or the local 0 format (0712345678)."
			).format(phone_number, country_code),
			RoyceTalkError,
		)

	if not PHONE_RE.fullmatch(normalized):
		frappe.throw(_("'{0}' doesn't look like a valid phone number").format(phone_number), RoyceTalkError)

	return normalized


def _safe_json(response) -> dict:
	try:
		return response.json()
	except ValueError:
		return {}


def _error_message(response, body: dict) -> str:
	if response.status_code == 403:
		return _("Invalid or missing RoyceTalk API key")
	if response.status_code == 429:
		return _("RoyceTalk rate limit exceeded. Please retry shortly.")
	return body.get("error") or body.get("message") or _("RoyceTalk request failed ({0})").format(
		response.status_code
	)
