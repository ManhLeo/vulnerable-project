"""
Security response headers middleware.

Applied to every response to harden the browser security posture.
Add / adjust headers in the single dict below — no code changes needed elsewhere.
"""
from __future__ import annotations

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response


_SECURITY_HEADERS: dict[str, str] = {
    # Prevent clickjacking
    "X-Frame-Options": "DENY",
    # Disable MIME-type sniffing
    "X-Content-Type-Options": "nosniff",
    # Control referrer information
    "Referrer-Policy": "strict-origin-when-cross-origin",
    # Restrict browser feature access — camera/mic/geolocation disabled
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    # Remove server fingerprint
    "X-Powered-By": "",
}


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Inject security headers on every outgoing response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        response: Response = await call_next(request)
        for header, value in _SECURITY_HEADERS.items():
            if value:  # Skip empty strings (e.g. X-Powered-By removal handled differently)
                response.headers[header] = value
            else:
                if header in response.headers:
                    del response.headers[header]
        return response
