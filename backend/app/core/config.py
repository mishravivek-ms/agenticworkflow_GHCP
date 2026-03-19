import os
import warnings

VALID_USERNAME = os.getenv("VALID_USERNAME", "username")
VALID_PASSCODE = os.getenv("VALID_PASSCODE", "passcode")

if "VALID_USERNAME" not in os.environ or "VALID_PASSCODE" not in os.environ:
    warnings.warn(
        "Using default credentials. Set VALID_USERNAME and VALID_PASSCODE for production.",
        RuntimeWarning,
    )
