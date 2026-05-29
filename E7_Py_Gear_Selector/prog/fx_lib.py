"""
Backward-compatible facade for e7_gear.

Existing scripts and notebooks can continue using `import fx_lib as fx`.
"""

from e7_gear import *  # noqa: F403
from e7_gear.settings import verify_settings

verify_setup = verify_settings
