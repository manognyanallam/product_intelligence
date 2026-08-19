"""
Shared rate limiter instance for the AI Product Intelligence Platform.

All routers import the single `limiter` instance from this module so that
rate-limit state is shared across the application. The limiter is registered
on the FastAPI app via `app.state.limiter`.

Reference: architecture_final.md §12 (Security Architecture)
"""
from slowapi import Limiter
from slowapi.util import get_remote_address

# Single shared limiter keyed by client IP address.
limiter = Limiter(key_func=get_remote_address)

