# Security

The supported version is the current `main` deployment at bibliothecacatholica.com. The application is static, has no site login or database, and stores reader notes in the reader's own browser. Analytics and outside services have their own behavior, disclosed on the site's Privacy & Analytics page.

For a suspected vulnerability, avoid a public issue containing exploit details, personal information, or reader notes. Use GitHub's private vulnerability reporting if offered on the repository's Security page. Otherwise contact the maintainer privately at micahwatson@bibliothecacatholica.com with the affected URL, build ID, reproduction steps, and likely impact. No response-time commitment is promised. Do not perform destructive testing or scan third-party libraries.

## Current controls and limits

- CI has read-only repository permissions, pinned action commits, deterministic catalog/static builds, and automated tests.
- The boot guard retains plain pages and recovery links when interactive code cannot start.
- Outbound URLs in catalog source fields are checked for HTTP(S) schemes. Remote HTML is not fetched as part of ordinary site search.
- The HTML declares a strict-origin-when-cross-origin referrer policy.
- Cloudflare Pages serves the site and applies `_headers`: site-wide `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, a `Permissions-Policy` that turns off camera, microphone, geolocation, payment, USB, serial, Bluetooth, and topics, and an enforced Content-Security-Policy (with `frame-ancestors 'self'`) that lists the scripts, analytics, fonts, and reader requests the site uses (#83); `*.pages.dev` previews also get `X-Robots-Tag: noindex`. `tests/test_analytics.py` checks the file. Change the CSP only after testing the affected pages.
- Secret scanning, push protection, private-reporting settings, and GA4 admin settings are account controls. Their presence is not established by repository files. See the verified audit notes for remaining work.
- Link-check scripts accept URLs from maintained snapshots and follow redirects. Do not run them against untrusted submissions without adding public-address validation for every request and redirect. They are not run automatically by CI.

Report ordinary broken source links using the public site-problem form. A rights complaint follows the site's Takedown page rather than the security process.
