"""Check definitions."""

from djcheckup.checks import (
    ContentCheck,
    CookieCheck,
    CookieHttpOnlyCheck,
    CookieSameSiteCheck,
    CookieSecureCheck,
    HeaderCheck,
    PathCheck,
    SchemeCheck,
    SeverityWeight,
)

admin_check = PathCheck(
    check_id="admin_check",
    name="Is your Django admin site exposed at the default URL?",
    path="/admin",
    success=False,
    severity=SeverityWeight.HIGH,
    success_message="""
Your Django admin site is not exposed at the default URL. This reduces the risk of automated attacks.
""",
    failure_message="""
Your Django admin site is accessible at the default URL (`/admin`).

Best practice is to restrict admin access to trusted IPs, use strong authentication, and change the admin URL to a
non-default, unguessable value. Never expose the admin over HTTP; always use HTTPS.

Reference:
- [Django Admin Docs](https://docs.djangoproject.com/en/stable/ref/contrib/admin/#adminsite-objects)
""",
)


csrf_check = CookieCheck(
    check_id="csrf_check",
    name="Is a CSRF cookie set?",
    cookie_name="csrftoken",
    success=True,
    severity=SeverityWeight.LOW,
    success_message="CSRF cookie detected. Your site is protected against cross-site request forgery attacks.",
    failure_message="""
No CSRF cookie was found. This is expected if your site does not render any forms that require CSRF protection on this
page. If you have forms that perform POST, PUT, or DELETE requests, ensure Django's CSRF middleware is enabled and not
bypassed.

Reference:
- [Django CSRF Protection](https://docs.djangoproject.com/en/stable/ref/csrf/)
""",
)


csrf_httponly_check = CookieHttpOnlyCheck(
    check_id="csrf_httponly_check",
    depends_on="csrf_check",
    name="Is the CSRF cookie HttpOnly?",
    cookie_name="csrftoken",
    success=True,
    severity=SeverityWeight.MEDIUM,
    success_message="Your CSRF cookie is marked as HttpOnly, which helps prevent some XSS attacks.",
    failure_message="""
Your CSRF cookie is not marked as HttpOnly. While Django does not set this by default
(to allow JavaScript access for some use cases), setting HttpOnly can help mitigate certain XSS risks.
Consider your application's needs before enabling this.

**Note:** This check will be skipped if the `csrf_check` check fails.

Reference:
- [Django CSRF Cookie Settings](https://docs.djangoproject.com/en/stable/ref/settings/#csrf-cookie-httponly)
""",
)


csrf_samesite_check = CookieSameSiteCheck(
    check_id="csrf_samesite_check",
    depends_on="csrf_check",
    name="Is the CSRF cookie SameSite=Lax?",
    cookie_name="csrftoken",
    samesite_value="Lax",
    success=True,
    severity=SeverityWeight.HIGH,
    success_message="CSRF cookie is marked as SameSite=Lax, which helps prevent CSRF attacks via cross-site requests.",
    failure_message="""
Your CSRF cookie is not marked as SameSite=Lax. This increases the risk of CSRF attacks.
Set `CSRF_COOKIE_SAMESITE = 'Lax'` in your Django settings.

**Note:** This check will be skipped if the `csrf_check` check fails.

Reference:
- [Django CSRF Settings](https://docs.djangoproject.com/en/stable/ref/settings/#csrf-cookie-samesite)
""",
)


csrf_secure_check = CookieSecureCheck(
    check_id="csrf_secure_check",
    depends_on="csrf_check",
    name="Is the CSRF cookie Secure?",
    cookie_name="csrftoken",
    success=True,
    severity=SeverityWeight.HIGH,
    success_message="CSRF cookie is marked as Secure. It will only be sent over HTTPS.",
    failure_message="""
Your CSRF cookie is not marked as Secure. This means it could be sent over unencrypted HTTP,
exposing it to interception. Set `CSRF_COOKIE_SECURE = True` in your Django settings.

**Note:** This check will be skipped if the `csrf_check` check fails.

Reference:
- [Django CSRF Settings](https://docs.djangoproject.com/en/stable/ref/settings/#csrf-cookie-secure)
""",
)


debug_404_check = PathCheck(
    check_id="debug_404_check",
    name="Does your site return a 404 for non-existent pages?",
    path="/a/b/c/d/e/f/g/h/i/j/xyz/",
    status_code=404,
    success=True,
    severity=SeverityWeight.MEDIUM,
    success_message="Your site correctly returns a 404 error for non-existent pages.",
    failure_message="""
Your site does not return a 404 error for non-existent pages. This may indicate a misconfiguration or a custom error
handler that does not set the correct status code.
Ensure your web server and Django app return 404 for missing resources.

Reference:
- [Django Custom Error Views](https://docs.djangoproject.com/en/stable/topics/http/views/#customizing-error-views)
""",
)


debug_check = ContentCheck(
    check_id="debug_check",
    depends_on="debug_404_check",
    name="Is Django DEBUG mode disabled?",
    path="/a/b/c/d/e/f/g/h/i/j/xyz/",
    content="DEBUG = True",
    success=False,
    severity=SeverityWeight.CRITICAL,
    success_message="Django DEBUG mode is disabled. This is essential for production security.",
    failure_message="""
Your site appears to have Django's DEBUG mode enabled. This exposes sensitive information and should never be used in
production. Set `DEBUG = False` in your settings.

Reference:
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/#debug)
""",
)


hsts_header_check = HeaderCheck(
    check_id="hsts_header_check",
    name="Is the Strict-Transport-Security (HSTS) header set?",
    header_name="Strict-Transport-Security",
    success=True,
    severity=SeverityWeight.HIGH,
    success_message="Strict-Transport-Security header is set. Your site enforces HTTPS for all visitors.",
    failure_message="""
Your site does not send the Strict-Transport-Security (HSTS) header. This means browsers may allow users to visit your
site over HTTP, exposing them to downgrade attacks.
Set this header in your web server or via Django's `SECURE_HSTS_SECONDS` setting.

Reference:
- [Django Security Settings](https://docs.djangoproject.com/en/stable/ref/settings/#secure-hsts-seconds)
- [MDN: Strict-Transport-Security](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security)
""",
)


http_check = SchemeCheck(
    check_id="http_check",
    name="Does your site redirect all HTTP traffic to HTTPS?",
    start_scheme="http",
    end_scheme="https",
    success=True,
    severity=SeverityWeight.HIGH,
    success_message="All HTTP traffic is redirected to HTTPS. This is essential for security.",
    failure_message="""
Your site does not redirect HTTP traffic to HTTPS. This exposes users to man-in-the-middle attacks. Ensure your web
server or CDN is configured to redirect all HTTP requests to HTTPS.

Reference:
- [Django Security Settings](https://docs.djangoproject.com/en/stable/ref/settings/#secure-ssl-redirect)
- [Google Web Fundamentals](https://developers.google.com/web/fundamentals/security/encrypt-in-transit/enable-https)
""",
)


https_check = SchemeCheck(
    check_id="https_check",
    name="Is your site accessible via HTTPS?",
    start_scheme="https",
    end_scheme="https",
    success=True,
    severity=SeverityWeight.HIGH,
    success_message="Your site is accessible via HTTPS. All sensitive data is encrypted in transit.",
    failure_message="""
Your site is not accessible via HTTPS. This exposes all traffic to interception and tampering. Obtain and install a
valid TLS certificate and configure your web server to serve HTTPS.

Reference:
- [Django Security Settings](https://docs.djangoproject.com/en/stable/ref/settings/#secure-proxy-ssl-header)
- [Cloudflare SSL](https://support.cloudflare.com/hc/en-us/articles/360023792171-Getting-Started-with-Cloudflare-SSL)
""",
)


login_check = PathCheck(
    check_id="login_check",
    name="Is your login page exposed at a default or guessable URL?",
    path="/accounts/login",
    success=False,
    severity=SeverityWeight.MEDIUM,
    success_message="Login page is not exposed at the default URL. This reduces the risk of automated attacks.",
    failure_message="""
Your login page is accessible at the default URL (`/accounts/login/`). Consider changing it to a non-default path and
always require HTTPS for login forms. Use strong authentication and rate limiting to prevent brute-force attacks.
""",
)


sessionid_cookie_check = CookieCheck(
    check_id="sessionid_cookie_check",
    name="Is the sessionid cookie set?",
    cookie_name="sessionid",
    success=True,
    severity=SeverityWeight.LOW,
    success_message="Session cookie is set. User sessions are being managed securely.",
    failure_message="""
No sessionid cookie was found. This is normal if your site does not use sessions on this page. If your application
relies on sessions for authentication or user data, ensure Django's session middleware is enabled and configured
correctly.

Reference:
- [Django Sessions](https://docs.djangoproject.com/en/stable/topics/http/sessions/)
""",
)


sessionid_httponly_check = CookieHttpOnlyCheck(
    check_id="sessionid_httponly_check",
    depends_on="sessionid_cookie_check",
    name="Is the sessionid cookie HttpOnly?",
    cookie_name="sessionid",
    success=True,
    severity=SeverityWeight.HIGH,
    success_message="Sessionid cookie is marked as HttpOnly. This helps prevent access from JavaScript.",
    failure_message="""
Your sessionid cookie is not marked as HttpOnly. This increases the risk of session theft via XSS.
Set `SESSION_COOKIE_HTTPONLY = True` in your Django settings.

**Note:** This check will be skipped if the `sessionid_cookie_check` check fails.

Reference:
- [Django Session Security](https://docs.djangoproject.com/en/stable/ref/settings/#session-cookie-httponly)
""",
)


sessionid_samesite_check = CookieSameSiteCheck(
    check_id="sessionid_samesite_check",
    depends_on="sessionid_cookie_check",
    name="Is the sessionid cookie SameSite=Lax?",
    cookie_name="sessionid",
    samesite_value="Lax",
    success=True,
    severity=SeverityWeight.HIGH,
    success_message="Sessionid cookie is marked as SameSite=Lax. This helps prevent CSRF attacks.",
    failure_message="""
Your sessionid cookie is not marked as SameSite=Lax. This increases the risk of CSRF attacks.
Set `SESSION_COOKIE_SAMESITE = 'Lax'` in your Django settings.

Reference:
- [Django Session Security](https://docs.djangoproject.com/en/stable/ref/settings/#session-cookie-samesite)
""",
)


sessionid_secure_check = CookieSecureCheck(
    check_id="sessionid_secure_check",
    depends_on="sessionid_cookie_check",
    name="Is the sessionid cookie Secure?",
    cookie_name="sessionid",
    success=True,
    severity=SeverityWeight.HIGH,
    success_message="Sessionid cookie is marked as Secure. It will only be sent over HTTPS.",
    failure_message="""
Your sessionid cookie is not marked as Secure. This means it could be sent over unencrypted HTTP, exposing it to
interception. Set `SESSION_COOKIE_SECURE = True` in your Django settings.

**Note:** This check will be skipped if the `sessionid_cookie_check` check fails.

Reference:
- [Django Session Security](https://docs.djangoproject.com/en/stable/ref/settings/#session-cookie-secure)
""",
)


xframe_header_check = HeaderCheck(
    check_id="xframe_header_check",
    name="Is the X-Frame-Options header set?",
    header_name="X-Frame-Options",
    success=True,
    severity=SeverityWeight.HIGH,
    success_message="X-Frame-Options header is set. Your site is protected against clickjacking attacks.",
    failure_message="""
Your site does not send the X-Frame-Options header. This allows your site to be embedded in iframes,
making it vulnerable to clickjacking. Set this header in your web server or via Django's `XFrameOptionsMiddleware`.

Reference:
- [Django Clickjacking Protection](https://docs.djangoproject.com/en/stable/ref/clickjacking/)
- [MDN: X-Frame-Options](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options)
""",
)


all_checks = [
    admin_check,
    csrf_check,
    csrf_httponly_check,
    csrf_samesite_check,
    csrf_secure_check,
    debug_404_check,
    debug_check,
    hsts_header_check,
    http_check,
    https_check,
    login_check,
    sessionid_cookie_check,
    sessionid_httponly_check,
    sessionid_secure_check,
    sessionid_samesite_check,
    xframe_header_check,
]
