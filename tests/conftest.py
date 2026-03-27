"""Fixtures for HA Alert tests."""
from __future__ import annotations

import sys
from datetime import datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

# ---------------------------------------------------------------------------
# Mock homeassistant modules BEFORE any other imports so that decorators and
# utility functions resolve correctly when the production modules are loaded.
# ---------------------------------------------------------------------------

def _make_mock(name: str) -> MagicMock:
    mod = MagicMock()
    mod.__name__ = name
    mod.__path__ = [name]
    mod.__package__ = name
    mod.__spec__ = None
    return mod


_HA_MODS = [
    "homeassistant",
    "homeassistant.core",
    "homeassistant.components",
    "homeassistant.components.sensor",
    "homeassistant.config_entries",
    "homeassistant.helpers",
    "homeassistant.helpers.entity_platform",
    "homeassistant.helpers.event",
    "homeassistant.helpers.typing",
    "homeassistant.util",
    "homeassistant.util.dt",
    "homeassistant.exceptions",
    "voluptuous",
]

for _name in _HA_MODS:
    if _name not in sys.modules:
        sys.modules[_name] = _make_mock(_name)

# @callback must be a passthrough decorator, not a MagicMock, otherwise
# methods decorated with it get replaced by a MagicMock and stop working.
sys.modules["homeassistant.core"].callback = lambda f: f

# dt_util.utcnow must return a real datetime so timestamp comparisons (>=)
# and isoformat() calls work correctly in HAAlertManager.
# __init__.py does: from homeassistant.util import dt as dt_util
# That resolves to the .dt attribute on the util mock, which must be the same
# object as sys.modules["homeassistant.util.dt"] so the utcnow fix applies.
_dt_mock = sys.modules["homeassistant.util.dt"]
_dt_mock.utcnow = lambda: datetime.now(timezone.utc)
sys.modules["homeassistant.util"].dt = _dt_mock

# ---------------------------------------------------------------------------

import pytest
from homeassistant.core import HomeAssistant


@pytest.fixture
def mock_hass():
    """Return a mock HomeAssistant instance."""
    hass = MagicMock(spec=HomeAssistant)
    hass.data = {}
    hass.services = MagicMock()
    hass.services.async_register = MagicMock()
    hass.services.async_remove = MagicMock()
    hass.config_entries = MagicMock()
    hass.config_entries.async_forward_entry_setups = AsyncMock(return_value=True)
    hass.config_entries.async_unload_platforms = AsyncMock(return_value=True)
    hass.states = MagicMock()
    return hass


@pytest.fixture
def mock_entry():
    """Return a mock config entry."""
    entry = MagicMock()
    entry.entry_id = "test_entry_id"
    entry.runtime_data = None
    return entry
