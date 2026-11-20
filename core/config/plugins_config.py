# --- DNK-MRH-HEADER ---
# mrh_id: "core/config/plugins_config.py"
# purpose: "Configuration file for dynamic Plugin System"
# author: "DNK-e.com Maksym"
# license: "MIT"
# status: "Active"
# version: "1.0.0"
# updated_at: "2026-08-12"
# --- END DNK-MRH-HEADER ---

import os
from typing import List

_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
_default_plugins_dir = os.path.join(_root, "packages", "plugins")
if not os.path.exists(_default_plugins_dir):
    _default_plugins_dir = os.path.join(_root, "plugins")

PLUGINS_DIR: str = os.getenv("PLUGINS_DIR", _default_plugins_dir)

# List of enabled plugin names, defaults to empty (meaning load all or none by default)
# For testing and production we can enable specific plugins
ENABLED_PLUGINS: List[str] = os.getenv("ENABLED_PLUGINS", "").split(",")
if ENABLED_PLUGINS == [""]:
    ENABLED_PLUGINS = []

# Initialization timeout limits
PLUGIN_TIMEOUT_SECONDS: int = int(os.getenv("PLUGIN_TIMEOUT_SECONDS", "30"))
