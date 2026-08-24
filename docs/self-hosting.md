# Self-hosting installation

This page is for people running their own bench (not installing via the Frappe Cloud
Marketplace — if that's you, just click **Install App** on your site from the listing
instead and skip this whole page).

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app https://github.com/royceltd/en_royce_talk --branch version-16
bench install-app royce_talk
```

The repo is public, so this works from any machine with network access — no GitHub
authentication required.

Note: the repo is named `en_royce_talk`, but the installed app is still `royce_talk`
(that's expected — see the "Repo name vs. app name" note in the main
[README](../README.md)).
