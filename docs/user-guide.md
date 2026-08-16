# Kenya SMS by RoyceTalk — User Guide

This guide is for the person setting up and using SMS in your Frappe/ERPNext site — no
coding required. If you're looking for technical/developer details instead, see the
main [README](../README.md).

## What this app does

Once installed, your ERPNext site can send SMS through [RoyceTalk](https://roycetalk.com)
in three ways:

1. **One-off notifications** — a "Notify Customer" button on Sales Invoice and Sales
   Order that texts a customer directly from the document.
2. **Marketing campaigns** — bulk SMS to your Customers and Leads, with consent rules
   built in so you can't accidentally text someone who hasn't agreed to receive
   marketing messages.
3. **Operational broadcasts** — bulk SMS to your Employees and Suppliers (shift
   changes, purchase order updates, etc.) — separate from marketing, since it's
   internal communication, not advertising.

Every message sent, however it was triggered, is logged in one place so you can see
what went out, to whom, and what it cost.

## 1. Get your RoyceTalk API key

1. Go to [roycetalk.com/dashboard/api-keys](https://roycetalk.com/dashboard/api-keys)
   and log in to your RoyceTalk account.
2. Copy your API key (it looks like `XXXX_XXXXXXXXXXXXXXXXXXXXXXXX_`).
3. Note your **Sender ID** too — this is the name recipients see as the sender, and it
   must already be approved/registered on your RoyceTalk account before you can use it
   here.

## 2. Set up RoyceTalk Settings

In your ERPNext site, search for **RoyceTalk Settings** in the awesomebar (top search
bar) or find it under the **Royce Talk** workspace on the Desk home page.

1. Paste your **API Key** and **Default Sender ID** from step 1.
2. Leave **API Base URL** as `https://roycetalk.com` unless RoyceTalk support tells you
   otherwise.
3. Enter a **Test Phone Number** (your own number is a good choice) and click
   **Send Test SMS**. You should receive a text within a few seconds — if you don't,
   check the error message shown and re-check your API key/Sender ID.
4. Save the form. A **Callback URL** will appear automatically — copy this into your
   RoyceTalk dashboard so delivery status (delivered/failed) flows back into this app.

That's the minimum setup. Everything below is optional, turn on what you need.

### Optional: use RoyceTalk for the rest of the system too

If you check **"Use as Site-wide SMS Gateway"**, RoyceTalk also becomes the transport
for any built-in ERPNext feature that sends SMS — Notifications configured with the
"SMS" channel, for example. Off by default; turn on only once you understand this also
affects ERPNext's own **SMS Center** tool (see the warning banner that appears there
once this is on — it explains why SMS Center should generally be avoided in favor of
RoyceTalk SMS Campaign, further down this guide).

### Optional: low balance alerts

Set a **Low Balance Alert Threshold** (in SMS units) on the same Settings page. Once
your RoyceTalk balance drops below that number, every System Manager on your site gets
an email — so you find out before sends start failing, not after.

## 3. Sending a one-off SMS from a document

Open any submitted **Sales Invoice** or **Sales Order**. Under the **SMS** button
group, click **Notify Customer**. A dialog opens with the customer's phone number and
a suggested message pre-filled — edit either and click **Send**.

## 4. Sending a marketing campaign (Customers / Leads)

Go to **RoyceTalk SMS Campaign** (in the Royce Talk workspace) and click **New**.

1. **Send To** — choose **Customer** or **Lead**.
   - For **Customer**, only contacts with the **SMS Marketing Consent** checkbox
     enabled on their Contact record will ever be included. This is off by default —
     you (or the customer) need to explicitly turn it on per contact before they can
     receive marketing SMS.
   - For **Lead**, leads are included by default unless someone has checked their
     **Opted Out of SMS** checkbox, or their status is "Do Not Contact". This is a
     different rule from Customers on purpose — see the note at the end of this
     section.
2. Optionally narrow the audience with **Customer** / **Customer Group** / **Territory**
   (Customers) or **Territory** / **Lead Status** (Leads).
3. Write your **Message**.
4. Click **Preview Recipients & Cost** — this tells you exactly how many people will
   receive it and roughly what it will cost, before you commit to anything.
5. When you're happy, click **Submit**. The system will refuse to send (with a clear
   reason) if RoyceTalk isn't set up, if nobody matches your filters, or if the
   estimated cost is more than your current RoyceTalk balance.
6. Sending happens in the background — refresh the page after a minute to see the
   final results (how many were sent, how many failed, the actual cost).

> **A note on the Lead opt-out rule:** Leads are included by default, which is a
> weaker consent standard than Customers get. This was a deliberate choice, not an
> oversight — but if SMS marketing to Leads matters for your business, it's worth
> getting your own legal opinion on whether that satisfies Kenya's Data Protection Act
> for your specific situation before relying on it at real volume.

## 5. Sending an operational broadcast (Employees / Suppliers)

Go to **RoyceTalk Operational Broadcast** and click **New**. Same flow as a campaign —
pick **Employee** or **Supplier**, narrow by Department/Branch/Status or
Supplier/Supplier Group, preview, then submit. There's no consent checkbox here on
purpose: this is for internal/operational messages (a shift change, a purchase order
update), not marketing, so it doesn't carry the same rules. Don't use this tool for
anything customer-facing — that's what SMS Campaign is for.

## 6. Checking what was sent

**RoyceTalk SMS Log** has one row per message ever sent — recipient, status, cost,
and (if it failed) why. The Royce Talk workspace home page also shows three live
numbers: SMS sent this month, spend this month, and failures this month, so you don't
need to open the log just to check those.

## Getting help

If a send fails and the error message isn't clear, check **RoyceTalk SMS Log** first —
every failure is recorded with RoyceTalk's own error message. For account-level
issues (balance, sender ID approval, API key problems), contact RoyceTalk support
directly through your [RoyceTalk dashboard](https://roycetalk.com/dashboard).
