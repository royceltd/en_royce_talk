### Royce Talk

Send SMS notifications to customers via the Royce Talk SMS API

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch version-16
bench install-app royce_talk
```
<!-- n8nh7zItQm04 -->
### What this app does

Installs a RoyceTalk SMS integration for your Frappe/ERPNext site:

- **RoyceTalk Settings** (single doctype) — enter your RoyceTalk API key and default
  Sender ID. Includes a "Send Test SMS" button for onboarding.
- **RoyceTalk SMS Log** — every SMS sent through this app is logged here (recipient,
  status, RoyceTalk message id, cost, units, error) and can be linked back to any
  document (Sales Invoice, Customer, etc.) via `reference_doctype`/`reference_name`.
- **`royce_talk.royce_talk.utils.send_single_sms(...)`** — whitelisted function to call
  from a client script button, a server script, or another app. Also `queue_sms(...)`
  for the same call fired from a document event without blocking the save.
- **Site-wide SMS gateway (optional)** — enable "Use as Site-wide SMS Gateway" on
  RoyceTalk Settings to route Frappe's built-in Notification "SMS" channel and OTP/2FA
  messages through RoyceTalk too, with no extra code.
- **Delivery webhook** — `RoyceTalk Settings` shows a Callback URL to paste into your
  RoyceTalk dashboard so delivery status updates flow back into RoyceTalk SMS Log.
- **Royce Talk workspace** — icon + shortcuts to Settings and SMS Log on the Desk home page.
- **"Notify Customer" button on Sales Invoice** — shipped as a Client Script (no JS
  build step required), opens a dialog pre-filled with the invoice's contact number and
  a default message, sends via `send_single_sms`, and logs against the invoice.
- **Sample Notification template** — a ready-to-enable Notification record
  ("RoyceTalk - Sales Invoice Submitted (SMS)") that texts the customer on Sales
  Invoice submit. Shipped **disabled** on purpose — review the message and turn it on
  from Notification list once you're happy with it.
- **Kenyan phone normalization** — accepts `0712345678`, `254712345678`, and
  `+254712345678` interchangeably (configurable "Default Country Code" in Settings for
  other markets); numbers already in another country's `+` format pass through untouched.
- **Balance monitoring** — RoyceTalk Settings shows your current SMS balance (cached,
  with a "Check Balance Now" button), and an hourly scheduled job emails all System
  Managers once when it drops below the configurable threshold, so sends failing due to
  an empty wallet is something you get warned about, not something you discover later.
- **"Notify Customer" on Sales Order too**, same pattern as Sales Invoice.
- **RoyceTalk SMS Campaign** — marketing/bulk SMS to **Customers and Leads**, via
  RoyceTalk's native bulk endpoint (not a loop over single sends). Submittable
  doctype, with a **"Send To" selector** and two different consent models by explicit
  design, not oversight:
  - **Customer** — gated on `royce_talk_sms_consent` (Contact), **opted out by
    default**. A Contact is only ever included if someone explicitly checked that box.
  - **Lead** — gated on `royce_talk_sms_opted_out` (Lead), **opted in by default**. A
    Lead is included unless individually opted out, or their status is "Do Not
    Contact" (always excluded regardless of the opt-out field). This is a weaker
    consent posture than Customer's, chosen deliberately — worth your own legal read
    on Kenya's DPA if you rely on it for real marketing sends.
  - **Targeting**: Customer / Customer Group / Territory for Customers; Territory /
    Lead Status for Leads — matching the granularity of ERPNext's built-in SMS Center.
  - **"Preview Recipients & Cost"** button shows exact recipient count and an estimated
    cost before you commit to anything.
  - **Submit is blocked** (not just warned) if RoyceTalk isn't configured, if no
    recipients match the filters, or if the estimated cost exceeds your current
    RoyceTalk balance — checked live at submit time.
  - Sending itself runs as a background job (`frappe.enqueue`) so submitting doesn't
    block on a large campaign's HTTP calls; results (batch id, queued/failed counts,
    actual cost, balance after) are written back onto the campaign once done.
- **RoyceTalk Operational Broadcast** — a **separate** doctype/menu from SMS Campaign,
  for **Employees and Suppliers**. Internal/operational messaging, not marketing, so
  **no consent gating applies at all** — don't confuse this with the Campaign tool.
  Same "Send To" selector pattern, targeting Company/Department/Branch/Status for
  Employees or Supplier/Supplier Group for Suppliers. Shares the same
  preview/guardrail/background-send mechanics as SMS Campaign
  (`royce_talk/royce_talk/bulk_send.py`) minus the consent logic, which is
  doctype-specific and lives in `campaign.py` (Customer/Lead) vs `operational.py`
  (Employee/Supplier) respectively — kept as two files/doctypes on purpose so the very
  different consent rules for marketing vs internal audiences can never accidentally
  bleed into each other.
- **Known v1 limits on both bulk-send tools:** no per-recipient message
  personalization (RoyceTalk's bulk endpoint takes one message for the whole batch)
  and no per-recipient delivery tracking (only aggregate counts) — both are natural
  follow-ups if you need them.

### Known limitations (read before relying on this for OTP/2FA)

- RoyceTalk requires phone numbers in international format (`+254...`). If your users'
  mobile numbers aren't stored with a country code, sends will fail validation rather
  than silently going to the wrong country — check RoyceTalk SMS Log / Error Log.
- The delivery webhook has no documented signature/HMAC verification from RoyceTalk
  yet, so it's treated as informational only. Confirm with RoyceTalk support before
  trusting it for anything security-sensitive.
- **ERPNext's built-in SMS Center bypasses RoyceTalk SMS Campaign's consent gate.**
  SMS Center sends through the same core `send_sms()` function our site-wide gateway
  hook overrides, so once "Use as Site-wide SMS Gateway" is on, SMS Center becomes a
  working (but completely un-gated) bulk sender via RoyceTalk. We ship a client script
  that shows a warning and hides SMS Center's Send button whenever the site-wide
  gateway is active, steering users to RoyceTalk SMS Campaign instead — but this is a
  UI nudge, not a permission change (SMS Center is already System Manager-only by
  default, same as our own doctypes).
- **Lead consent is opt-out, not opt-in — a deliberate, explicit product decision,
  not a compliance recommendation.** I'm not a lawyer; if Lead SMS marketing matters
  to your business, get your own legal read on whether an opt-out model satisfies
  Kenya's Data Protection Act for your use case before relying on it at scale.

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/royce_talk
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

mit
