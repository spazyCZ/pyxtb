"""
pyxtb package.

Provides an interface to interact with the XTB trading API, allowing users to manage trades,
retrieve market data, and handle account information.

Modules:
    _types: Defines data types and enums used across the API.
    api: Main API connector class for interacting with XTB services.
    errors: Handles API error management.
"""

from ._types import *  # noqa: F403
from .api import Api  # noqa: F401
