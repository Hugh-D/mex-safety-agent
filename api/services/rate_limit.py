from slowapi import Limiter
from slowapi.util import get_remote_address

# Shared limiter — imported by main.py (to register) and by routers (to decorate handlers).
# Default: 120/minute. AI/compliance routes override to 20/minute per IP.
limiter = Limiter(key_func=get_remote_address, default_limits=["120/minute"])
