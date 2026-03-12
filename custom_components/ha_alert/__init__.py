"""The HA Alert integration."""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry

type HAAlertConfigEntry = ConfigEntry[HAAlertManager]
from homeassistant.core import HomeAssistant, ServiceCall, callback
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.util import dt as dt_util

from .const import (
    ALERT_TYPES,
    ATTR_ALERTS,
    ATTR_LAST_UPDATED,
    CONF_ALERT_TYPE,
    CONF_CONDITION_ENTITY,
    CONF_CONDITION_STATE,
    CONF_ENTITY_ID,
    CONF_MESSAGE,
    CONF_REPEAT_INTERVAL,
    CONF_REPEAT_UNTIL,
    CONF_TITLE,
    DOMAIN,
    SERVICE_ACKNOWLEDGE,
    SERVICE_CREATE,
    SERVICE_DISMISS,
)

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]

SERVICE_CREATE_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_ALERT_TYPE): vol.In(ALERT_TYPES),
        vol.Required(CONF_MESSAGE): cv.string,
        vol.Optional(CONF_TITLE): cv.string,
        vol.Optional(CONF_ENTITY_ID): cv.entity_id,
        vol.Optional(CONF_REPEAT_INTERVAL): vol.All(vol.Coerce(int), vol.Range(min=0, max=1440)),
        vol.Optional(CONF_REPEAT_UNTIL): cv.string,
        vol.Optional(CONF_CONDITION_ENTITY): cv.entity_id,
        vol.Optional(CONF_CONDITION_STATE): cv.string,
    }
)

SERVICE_ALERT_ID_SCHEMA = vol.Schema(
    {
        vol.Required("alert_id"): cv.string,
    }
)


class HAAlertManager:
    """Manages all active alerts."""

    def __init__(self, hass: HomeAssistant) -> None:
        """Initialize the alert manager."""
        self.hass = hass
        self._alerts: dict[str, dict[str, Any]] = {}
        self._listeners: list[Any] = []
        self._repeat_task: asyncio.Task | None = None
        self._state_unsubs: dict[str, Any] = {}

    @property
    def alerts(self) -> list[dict[str, Any]]:
        """Return list of active alerts."""
        return list(self._alerts.values())

    def create_alert(self, data: dict[str, Any]) -> str:
        """Create a new alert and return its ID."""
        alert_id = f"alert_{int(time.time() * 1000)}_{uuid.uuid4().hex[:6]}"
        now = dt_util.utcnow().isoformat()

        alert = {
            "id": alert_id,
            "type": data[CONF_ALERT_TYPE],
            "message": data[CONF_MESSAGE],
            "title": data.get(CONF_TITLE),
            "created_at": now,
            "repeat_interval": data.get(CONF_REPEAT_INTERVAL) * 60 if data.get(CONF_REPEAT_INTERVAL) else None,
            "repeat_until": data.get(CONF_REPEAT_UNTIL),
            "next_repeat": None,
            "condition_entity": data.get(CONF_CONDITION_ENTITY),
            "condition_state": data.get(CONF_CONDITION_STATE),
            "acknowledged": False,
            "acknowledged_at": None,
        }

        if alert["repeat_interval"]:
            next_dt = dt_util.utcnow().replace(tzinfo=timezone.utc)
            alert["next_repeat"] = (
                next_dt.timestamp() + alert["repeat_interval"]
            )

        self._alerts[alert_id] = alert

        # Set up auto-dismiss listener
        if alert.get("condition_entity") and alert.get("condition_state"):
            self._setup_condition_listener(alert_id, alert["condition_entity"], alert["condition_state"])

        self._notify_listeners()
        _LOGGER.debug("Created alert %s: %s", alert_id, data[CONF_MESSAGE])
        return alert_id

    def dismiss_alert(self, alert_id: str) -> bool:
        """Dismiss (remove) an alert."""
        if alert_id in self._alerts:
            self._cleanup_condition_listener(alert_id)
            del self._alerts[alert_id]
            self._notify_listeners()
            _LOGGER.debug("Dismissed alert %s", alert_id)
            return True
        return False

    def acknowledge_alert(self, alert_id: str) -> bool:
        """Acknowledge an alert."""
        if alert_id in self._alerts:
            self._alerts[alert_id]["acknowledged"] = True
            self._alerts[alert_id]["acknowledged_at"] = dt_util.utcnow().isoformat()
            self._notify_listeners()
            _LOGGER.debug("Acknowledged alert %s", alert_id)
            return True
        return False

    def _setup_condition_listener(self, alert_id: str, entity_id: str, target_state: str) -> None:
        """Set up a state listener for auto-dismiss."""
        @callback
        def state_changed(event: Any) -> None:
            new_state = event.data.get("new_state")
            if new_state and new_state.state == target_state:
                self.dismiss_alert(alert_id)

        unsub = async_track_state_change_event(self.hass, entity_id, state_changed)
        self._state_unsubs[alert_id] = unsub

    def _cleanup_condition_listener(self, alert_id: str) -> None:
        """Remove a state listener."""
        if alert_id in self._state_unsubs:
            self._state_unsubs[alert_id]()
            del self._state_unsubs[alert_id]

    def add_listener(self, listener: Any) -> None:
        """Add a listener for alert changes."""
        self._listeners.append(listener)

    def remove_listener(self, listener: Any) -> None:
        """Remove a listener."""
        if listener in self._listeners:
            self._listeners.remove(listener)

    @callback
    def _notify_listeners(self) -> None:
        """Notify all listeners of changes."""
        for listener in self._listeners:
            try:
                listener()
            except Exception:  # noqa: BLE001
                _LOGGER.exception("Error notifying alert listener")

    async def async_check_repeats(self) -> None:
        """Check and process repeating alerts."""
        now = dt_util.utcnow().timestamp()
        changed = False

        for alert_id, alert in list(self._alerts.items()):
            if not alert.get("repeat_interval") or alert.get("next_repeat") is None:
                continue

            # Check if repeat_until has passed
            if alert.get("repeat_until"):
                try:
                    until_dt = datetime.fromisoformat(alert["repeat_until"])
                    if until_dt.tzinfo is None:
                        until_dt = until_dt.replace(tzinfo=timezone.utc)
                    if dt_util.utcnow() > until_dt:
                        continue
                except (ValueError, TypeError):
                    pass

            if now >= alert["next_repeat"]:
                # Reset acknowledged status and update next_repeat
                alert["acknowledged"] = False
                alert["acknowledged_at"] = None
                alert["next_repeat"] = now + alert["repeat_interval"]
                changed = True
                _LOGGER.debug("Repeating alert %s", alert_id)

        if changed:
            self._notify_listeners()

    async def async_start_repeat_task(self) -> None:
        """Start background task for repeating alerts."""
        self._repeat_task = asyncio.create_task(self._repeat_loop())

    async def _repeat_loop(self) -> None:
        """Background loop to handle repeating alerts."""
        while True:
            await asyncio.sleep(10)
            await self.async_check_repeats()

    def stop(self) -> None:
        """Stop the repeat task and clean up."""
        if self._repeat_task:
            self._repeat_task.cancel()
        for unsub in self._state_unsubs.values():
            unsub()
        self._state_unsubs.clear()


async def async_setup_entry(hass: HomeAssistant, entry: HAAlertConfigEntry) -> bool:
    """Set up HA Alert from a config entry."""
    manager = HAAlertManager(hass)
    entry.runtime_data = manager

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_create(call: ServiceCall) -> None:
        manager.create_alert(dict(call.data))

    async def handle_dismiss(call: ServiceCall) -> None:
        alert_id = call.data["alert_id"]
        if not manager.dismiss_alert(alert_id):
            _LOGGER.warning("Alert %s not found for dismissal", alert_id)

    async def handle_acknowledge(call: ServiceCall) -> None:
        alert_id = call.data["alert_id"]
        if not manager.acknowledge_alert(alert_id):
            _LOGGER.warning("Alert %s not found for acknowledgement", alert_id)

    hass.services.async_register(
        DOMAIN, SERVICE_CREATE, handle_create, schema=SERVICE_CREATE_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_DISMISS, handle_dismiss, schema=SERVICE_ALERT_ID_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_ACKNOWLEDGE, handle_acknowledge, schema=SERVICE_ALERT_ID_SCHEMA
    )

    await manager.async_start_repeat_task()

    return True


async def async_unload_entry(hass: HomeAssistant, entry: HAAlertConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        entry.runtime_data.stop()
        hass.services.async_remove(DOMAIN, SERVICE_CREATE)
        hass.services.async_remove(DOMAIN, SERVICE_DISMISS)
        hass.services.async_remove(DOMAIN, SERVICE_ACKNOWLEDGE)

    return unload_ok
