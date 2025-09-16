# DJ Checkup CLI

## Installation

This works best when installed with `uv tool` or `pipx`.

```bash
# With uv:
uv tool install djcheckup-cli

# Or with pipx:
pipx install djcheckup-cli
```

You can also run the tool without installing it:

```bash
# With uvx:
uvx djcheckup-cli https://yourdjangosite.com
```

## Usage

Run the `djcheckup-cli` command-line utility followed by the URL of your Django site.

You'll see a nicely formatted report in your terminal:

```text
╭──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╮
│                                              DJCheckup Results Summary                                               │
│ ┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓ │
│ ┃ Check                                       ┃ Result  ┃ Message                                                  ┃ │
│ ┡━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┩ │
│ │ Can I connect to your site?                 │ Success │ I was able to connect to the site.                       │ │
│ ├─────────────────────────────────────────────┼─────────┼──────────────────────────────────────────────────────────┤ │
│ │ Is your admin site accessible?              │ Success │ You've done a great job hiding the Admin site from       │ │
│ │                                             │         │ probing bots.                                            │ │
│ ├─────────────────────────────────────────────┼─────────┼──────────────────────────────────────────────────────────┤ │
│ │ Is there a CSRF cookie set?                 │ Success │ We found a CSRF cookie on your website, which means      │ │
│ │                                             │         │ you're securing your forms correctly.                    │ │
│ ├─────────────────────────────────────────────┼─────────┼──────────────────────────────────────────────────────────┤ │
│ │ Is the CSRF cookie HttpOnly?                │ Failure │ Your CSRF cookie is not marked as HttpOnly. This is      │ │
│ │                                             │         │ considered a security risk as it can be accessed by      │ │
│ │                                             │         │ malicious JavaScript running in the browser.             │ │
│ │                                             │         │                                                          │ │
│ │                                             │         │ You will need to configure this with your web server or  │ │
│ │                                             │         │ if you are unable to modify your web server              │ │
│ │                                             │         │ configuration, consider using Cloudflare.                │ │
│ │                                             │         │                                                          │ │
│ │                                             │         │ Reference:                                               │ │
│ │                                             │         │                                                          │ │
│ │                                             │         │  • Django Docs                                           │ │
│ ├─────────────────────────────────────────────┼─────────┼──────────────────────────────────────────────────────────┤ │
│ │ Is the CSRF cookie SameSite?                │ Success │ Great, your CSRF cookie is marked as SameSite=Lax.       │ │
│ ├─────────────────────────────────────────────┼─────────┼──────────────────────────────────────────────────────────┤ │
│ │ Is the CSRF cookie secured?                 │ Success │ Great, your CSRF cookie is marked as Secure.             │ │
│ ├─────────────────────────────────────────────┼─────────┼──────────────────────────────────────────────────────────┤ │
│ │ DEBUG check                                 │ Skipped │ Check skipped due to failed or missing dependency:       │ │
│ │                                             │         │ debug_404_check                                          │ │
│ ├─────────────────────────────────────────────┼─────────┼──────────────────────────────────────────────────────────┤ │
│ │ Is the HSTS Header set?                     │ Success │ Nice, your site is looking extra secure with Strict      │ │
│ │                                             │         │ Transport Security configured in addition to HTTPS.      │ │
│ ├─────────────────────────────────────────────┼─────────┼──────────────────────────────────────────────────────────┤ │
│ │ Does your site redirect from HTTP to HTTPS? │ Success │ Excellent - your site automatically redirects HTTP       │ │
│ │                                             │         │ traffic to HTTPS.                                        │ │
│ ├─────────────────────────────────────────────┼─────────┼──────────────────────────────────────────────────────────┤ │
│ │ Is your site accessible with HTTPS?         │ Success │ Nice - your site is accessible with HTTPS.               │ │
│ ├─────────────────────────────────────────────┼─────────┼──────────────────────────────────────────────────────────┤ │
│ │ Is your login page accessible?              │ Success │ We couldn't find a login page on your website.           │ │
│ ├─────────────────────────────────────────────┼─────────┼──────────────────────────────────────────────────────────┤ │
│ │ Does the sessionid cookie exist?            │ Failure │ Your sessionid cookie is not set. This is considered a   │ │
│ │                                             │         │ security risk as it can lead to session fixation         │ │
│ │                                             │         │ attacks.                                                 │ │
│ │                                             │         │                                                          │ │
│ │                                             │         │ You will need to configure this with your web server or  │ │
│ │                                             │         │ if you are unable to modify your web server              │ │
│ │                                             │         │ configuration, consider using Cloudflare.                │ │
│ │                                             │         │                                                          │ │
│ │                                             │         │ Reference:                                               │ │
│ │                                             │         │                                                          │ │
│ │                                             │         │  • Django Docs                                           │ │
│ ├─────────────────────────────────────────────┼─────────┼──────────────────────────────────────────────────────────┤ │
│ │ Is the sessionid cookie HttpOnly?           │ Skipped │ Check skipped due to failed or missing dependency:       │ │
│ │                                             │         │ sessionid_cookie_check                                   │ │
│ ├─────────────────────────────────────────────┼─────────┼──────────────────────────────────────────────────────────┤ │
│ │ Is the sessionid cookie Secure?             │ Skipped │ Check skipped due to failed or missing dependency:       │ │
│ │                                             │         │ sessionid_cookie_check                                   │ │
│ ├─────────────────────────────────────────────┼─────────┼──────────────────────────────────────────────────────────┤ │
│ │ Is the sessionid cookie SameSite?           │ Skipped │ Check skipped due to failed or missing dependency:       │ │
│ │                                             │         │ sessionid_cookie_check                                   │ │
│ ├─────────────────────────────────────────────┼─────────┼──────────────────────────────────────────────────────────┤ │
│ │ Is the X-Frame Header set?                  │ Success │ Excellent - the X-Frame header will help prevent         │ │
│ │                                             │         │ clickjacking attacks on your website.                    │ │
│ └─────────────────────────────────────────────┴─────────┴──────────────────────────────────────────────────────────┘ │
╰──────────────────────────────────────────────────────────────────────────────────────────────────────────────────────╯
```
