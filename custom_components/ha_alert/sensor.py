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
from .const import (
    ALERT_TYPE_ERROR,
    ALERT_TYPE_WARNING,
    ALERT_TYPE_INFO,
    ALERT_TYPE_SUCCESS,
    ATTR_ALERTS,
    ATTR_LAST_UPDATED,
    DOMAIN,
    SENSOR_ACTIVE_ALERTS,
    SENSOR_ERROR_COUNT,
    SENSOR_WARNING_COUNT,
    SENSOR_INFO_COUNT,
    SENSOR_SUCCESS_COUNT,
)

_LOGGER = logging.getLogger(__name__)


_TYPE_SENSOR_MAP = [
    (ALERT_TYPE_ERROR,   "Error Alerts",   "mdi:alert-octagon",  SENSOR_ERROR_COUNT),
    (ALERT_TYPE_WARNING, "Warning Alerts", "mdi:alert",          SENSOR_WARNING_COUNT),
    (ALERT_TYPE_INFO,    "Info Alerts",    "mdi:information",    SENSOR_INFO_COUNT),
    (ALERT_TYPE_SUCCESS, "Success Alerts", "mdi:check-circle",   SENSOR_SUCCESS_COUNT),
]


async def async_setup_entry(
    hass: HomeAssistant,
    entry: HAAlertConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up HA Alert sensor."""
    manager = entry.runtime_data
    entry_id = entry.entry_id
    entities: list[SensorEntity] = [HAAlertSensor(manager, entry_id)]
    for alert_type, name, icon, sensor_key in _TYPE_SENSOR_MAP:
        entities.append(HAAlertTypeSensor(manager, entry_id, alert_type, name, icon, sensor_key))
    async_add_entities(entities)


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


class HAAlertTypeSensor(SensorEntity):
    """Sensor that tracks active alerts of a specific type."""

    _attr_has_entity_name = True
    _attr_native_unit_of_measurement = "alerts"

    def __init__(
        self,
        manager: HAAlertManager,
        entry_id: str,
        alert_type: str,
        name: str,
        icon: str,
        sensor_key: str,
    ) -> None:
        """Initialize the type sensor."""
        self._manager = manager
        self._alert_type = alert_type
        self._attr_name = name
        self._attr_icon = icon
        self._attr_unique_id = f"{DOMAIN}_{entry_id}_{sensor_key}"
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
        """Return number of active alerts of this type."""
        return sum(1 for a in self._manager.alerts if a["type"] == self._alert_type)
