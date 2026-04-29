# DJ Checkup

## Overview

DJ Checkup is a security scanner for Django sites. This package provides a command-line interface to run the security
checks against your Django site. These are the same checks that are used by the DJ Checkup website at
<https://djcheckup.com>.

## Installation

This works best when installed with `pipx` or `uv tool`.

```bash
# With pipx:
pipx install djcheckup

# Or with uv:
uv tool install djcheckup
```

With uv, you can also run the tool without installing it first:

```bash
# With uvx:
uvx djcheckup https://yourdjangosite.com
```

## Usage

Run the `djcheckup` command-line utility with the URL of your Django site.
This will make several outbound requests from your computer to the website you are checking.

After a few seconds, you'll see a nicely formatted report in your terminal:

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

## Advanced Usage

If you are trying to scan a website that uses a self-signed SSL certificate, or has another SSL issue that you want to
ignore, you can pass the `--insecure` flag to the command. This tells the HTTP client to ignore SSL errors.

If you want to return the output in JSON format, you can pass the `--output-json` flag to the command. This will output a
JSON response in your terminal which can be copied/pasted or piped into a file or other tools.

## API

The `djcheckup` library can also be imported into your own code as a library so you can incorporate the results into
your own tools.

In the following basic example, `result` is a `SiteCheckResultDict` typed dictionary. See `outputs.py` for
implementation details:

```python
from djcheckup import run_checks

result = run_checks("https://example.com")
```

When using `djcheckup` programmatically, you can swap out the HTTP client with your own client with any specific
configuration you require. By default, DJ Checkup uses the [HTTPXYZ](https://httpxyz.org/) library which is a fork of
[HTTPX](https://www.python-httpx.org/). You can create your own client (either HTTPX or HTTPXYZ) with your own
customisations and pass it to the `run_checks` method.

You can also change the output to return a JSON string response. See `api.py` for implementation details.

A full example could look like the following, which uses a custom HTTPX client and returns JSON:

```python
import httpx
from djcheckup import run_checks


client = httpx.Client(
    headers={"User-Agent": "My User Agent"},
    timeout=10.0,
    follow_redirects=True,
    verify=True,
)

result = run_checks("https://example.com", client=client, output_format="json")

print(result)
```

[![Published on Django Packages](https://img.shields.io/badge/Published%20on-Django%20Packages-0c3c26)](https://djangopackages.org/packages/p/djcheckup/)
