# DJ Checkup

## Overview

DJ Checkup is a security scanner for Django sites. This package provides a command-line interface to run the security
checks against your Django site. These are the same checks that are used by the DJ Checkup website at
<https://djcheckup.com>.

## Installation

This works best when installed with `uv tool` or `pipx`.

```bash
# With uv:
uv tool install djcheckup

# Or with pipx:
pipx install djcheckup
```

You can also run the tool without installing it:

```bash
# With uvx:
uvx djcheckup https://yourdjangosite.com
```

## Usage

Run the `djcheckup` command-line utility with the URL of your Django site.

You'll see a nicely formatted report in your terminal:

```text
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                     DJ Checkup Results for https://djcheckup.com                                     │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃ Check                                            ┃ Result     ┃ Message                                          ┃ │
│ ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩ │
│ │ Can I connect to your site?                      │ 🟢 Success │ Connected to your site successfully.             │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Is your Django admin site exposed at the default │ 🟢 Success │ Your Django admin site is not exposed at the     │ │
│ │ URL?                                             │            │ default URL. This reduces the risk of automated  │ │
│ │                                                  │            │ attacks.                                         │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Is a CSRF cookie set?                            │ 🟢 Success │ CSRF cookie detected. Your site is protected     │ │
│ │                                                  │            │ against cross-site request forgery attacks.      │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Is the CSRF cookie HttpOnly?                     │ 🟢 Success │ Your CSRF cookie is marked as HttpOnly, which    │ │
│ │                                                  │            │ helps prevent some XSS attacks.                  │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Is the CSRF cookie SameSite=Lax?                 │ 🟢 Success │ CSRF cookie is marked as SameSite=Lax, which     │ │
│ │                                                  │            │ helps prevent CSRF attacks via cross-site        │ │
│ │                                                  │            │ requests.                                        │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Is the CSRF cookie Secure?                       │ 🟢 Success │ CSRF cookie is marked as Secure. It will only be │ │
│ │                                                  │            │ sent over HTTPS.                                 │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Does your site return a 404 for non-existent     │ 🟢 Success │ Your site correctly returns a 404 error for      │ │
│ │ pages?                                           │            │ non-existent pages.                              │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Is Django DEBUG mode disabled?                   │ 🟢 Success │ Django DEBUG mode is disabled. This is essential │ │
│ │                                                  │            │ for production security.                         │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Is the Strict-Transport-Security (HSTS) header   │ 🟢 Success │ Strict-Transport-Security header is set. Your    │ │
│ │ set?                                             │            │ site enforces HTTPS for all visitors.            │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Does your site redirect all HTTP traffic to      │ 🟢 Success │ All HTTP traffic is redirected to HTTPS. This is │ │
│ │ HTTPS?                                           │            │ essential for security.                          │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Is your site accessible via HTTPS?               │ 🟢 Success │ Your site is accessible via HTTPS. All sensitive │ │
│ │                                                  │            │ data is encrypted in transit.                    │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Is your login page exposed at a default or       │ 🟢 Success │ Login page is not exposed at the default URL.    │ │
│ │ guessable URL?                                   │            │ This reduces the risk of automated attacks.      │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Is the sessionid cookie set?                     │ 🔴 Failure │ No sessionid cookie was found. This is normal if │ │
│ │                                                  │            │ your site does not use sessions on this page. If │ │
│ │                                                  │            │ your application relies on sessions for          │ │
│ │                                                  │            │ authentication or user data, ensure Django's     │ │
│ │                                                  │            │ session middleware is enabled and configured     │ │
│ │                                                  │            │ correctly.                                       │ │
│ │                                                  │            │                                                  │ │
│ │                                                  │            │ Reference:                                       │ │
│ │                                                  │            │                                                  │ │
│ │                                                  │            │  • Django Sessions                               │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Is the sessionid cookie HttpOnly?                │ 🟡 Skipped │ Check skipped due to failed or missing           │ │
│ │                                                  │            │ dependency: sessionid_cookie_check               │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Is the sessionid cookie Secure?                  │ 🟡 Skipped │ Check skipped due to failed or missing           │ │
│ │                                                  │            │ dependency: sessionid_cookie_check               │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Is the sessionid cookie SameSite=Lax?            │ 🟡 Skipped │ Check skipped due to failed or missing           │ │
│ │                                                  │            │ dependency: sessionid_cookie_check               │ │
│ ├──────────────────────────────────────────────────┼────────────┼──────────────────────────────────────────────────┤ │
│ │ Is the X-Frame-Options header set?               │ 🟢 Success │ X-Frame-Options header is set. Your site is      │ │
│ │                                                  │            │ protected against clickjacking attacks.          │ │
│ └──────────────────────────────────────────────────┴────────────┴──────────────────────────────────────────────────┘ │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
