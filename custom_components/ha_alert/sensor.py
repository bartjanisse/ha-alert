"""Sensor platform for HA Alert."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import dt as dt_util

from . import HAAlertConfigEntry, HAAlertManager
from .const import ATTR_ALERTS, ATTR_LAST_UPDATED, DOMAIN, SENSOR_ACTIVE_ALERTS

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HAAlertConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HA Alert sensor."""
    async_add_entities([HAAlertSensor(entry.runtime_data, entry.entry_id)])


class HAAlertSensor(SensorEntity):
    """Sensor that tracks all active alerts."""

    _attr_has_entity_name = True
    _attr_name = "Active Alerts"
    _attr_icon = "mdi:alert-circle-outline"
    _attr_native_unit_of_measurement = "alerts"

    def __init__(self, manager: HAAlertManager, entry_id: str) -> None:
        """Initialize the sensor."""
        self._manager = manager
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{SENSOR_ACTIVE_ALERTS}"
        self._last_updated: str | None = None

    async def async_added_to_hass(self) -> None:
        """Register as a listener for alert changes."""
        self._manager.add_listener(self._handle_update)

    async def async_will_remove_from_hass(self) -> None:
        """Unregister listener."""
        self._manager.remove_listener(self._handle_update)

    @callback
    def _handle_update(self) -> None:
        """Handle alert updates."""
        self._last_updated = dt_util.utcnow().isoformat()
        self.async_write_ha_state()

    @property
    def native_value(self) -> int:
        """Return number of active alerts."""
        return len(self._manager.alerts)

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the sensor attributes."""
        return {
            ATTR_ALERTS: self._manager.alerts,
            ATTR_LAST_UPDATED: self._last_updated or dt_util.utcnow().isoformat(),
        }
