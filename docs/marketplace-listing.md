# Frappe Cloud Marketplace — Listing Copy

Reference copy for the "Add from GitHub" → app profile step in the Frappe Cloud
dashboard (Settings → Become a Publisher → Marketplace → Add App). Not consumed by
the app itself — this is just so the listing content lives somewhere version-controlled
instead of only existing inside a form on frappe.io.

## App name

**Kenya SMS by RoyceTalk**

(Marketplace app names must be unique across the whole marketplace — worth
double-checking this hasn't been taken before submitting.)

## Short description (40–80 characters)

> SMS notifications and campaigns for ERPNext businesses in Kenya.

(65 characters — within the 40–80 range Frappe's guidelines ask for. One sentence,
doesn't repeat the app name per their guidance.)

## Long description (draft)

> Send SMS straight from ERPNext through RoyceTalk — transactional notifications,
> marketing campaigns, and internal broadcasts, all from documents and tools you
> already use.
>
> **One-off notifications** — a "Notify Customer" button on Sales Invoice and Sales
> Order sends a message in two clicks, logged automatically.
>
> **Marketing campaigns** — bulk SMS to Customers and Leads with consent rules built
> in, so a campaign can't accidentally reach someone who hasn't agreed to receive
> marketing messages. Preview exact recipient count and cost before every send.
>
> **Operational broadcasts** — a separate tool for internal messages to Employees and
> Suppliers, kept apart from marketing so the two are never confused.
>
> **Built for Kenyan phone numbers** — accepts local (07…), national (254…), and
> international (+254…) formats interchangeably.
>
> **Balance monitoring** — get emailed before your RoyceTalk balance runs out, not
> after a send silently fails.
>
> Every message is logged with delivery status, cost, and RoyceTalk's own message ID,
> whether it was sent from a button, a campaign, or ERPNext's own Notification system.

## Logo

`marketplace-logo.png` in this folder — 512×512, transparent corners, same green
message-bubble mark as the Desk app tile for brand consistency, redrawn at full
resolution rather than just upscaled from the 54×54 desk icon. Source is
`marketplace-logo.svg` if it ever needs edits (colors, resizing) — regenerate the PNG
with something like:

```bash
google-chrome --headless --disable-gpu --window-size=512,512 \
  --screenshot=marketplace-logo.png --default-background-color=00000000 \
  marketplace-logo.svg
```

## Still needed before submitting (not something I can generate for you)

- **Screenshots** — of RoyceTalk Settings, SMS Campaign preview, and the workspace
  dashboard cards would show the app's actual value well.
- **Support URL** — presumably something under roycetechnologies.co.ke.
- **Privacy Policy URL** — needs to exist somewhere public; I haven't seen one for
  Royce Technologies in this repo or mentioned anywhere in this conversation, so this
  may need to be written from scratch.
