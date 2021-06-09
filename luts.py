"""
Lookup tables & common reused bits for this app.
"""
import os

# This... actually looks like it's hardcoded almost everywhere, so, nuke?
unit_lu = {
    "temp": {"imperial": "°F", "metric": " °C"},
    "precip": {"imperial": "in", "metric": "mm"},
}

if os.environ.get("DASH_REQUESTS_PATHNAME_PREFIX"):
    path_prefix = os.getenv("DASH_REQUESTS_PATHNAME_PREFIX")
else:
    path_prefix = "/"
