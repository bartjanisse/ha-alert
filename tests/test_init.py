"""Tests for HA Alert __init__.py — HAAlertManager and setup."""
from __future__ import annotations

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock, patch, call

from custom_components.ha_alert import HAAlertManager
from custom_components.ha_alert.const import (
    CONF_ALERT_TYPE,
    CONF_MESSAGE,
    CONF_TITLE,
    CONF_REPEAT_INTERVAL,
    CONF_REPEAT_UNTIL,
    CONF_CONDITION_ENTITY,
    CONF_CONDITION_STATE,
)


# ---------------------------------------------------------------------------
# HAAlertManager — create_alert
# ---------------------------------------------------------------------------

class TestCreateAlert:
    """Tests for HAAlertManager.create_alert."""

    def setup_method(self):
        self.hass = MagicMock()
        self.hass.data = {}
        self.manager = HAAlertManager(self.hass)

    def test_create_minimal_alert(self):
        """A minimal alert is created with required fields only."""
        alert_id = self.manager.create_alert({
            CONF_ALERT_TYPE: "warning",
            CONF_MESSAGE: "Test bericht",
        })

        assert alert_id is not None
        assert alert_id.startswith("alert_")
        assert len(self.manager.alerts) == 1

        alert = self.manager.alerts[0]
        assert alert["type"] == "warning"
        assert alert["message"] == "Test bericht"
        assert alert["title"] is None
        assert alert["acknowledged"] is False
        assert alert["repeat_interval"] is None
        assert alert["condition_entity"] is None

    def test_create_alert_with_title(self):
        """An alert with a title stores the title correctly."""
        self.manager.create_alert({
            CONF_ALERT_TYPE: "error",
            CONF_MESSAGE: "Pomp uitgevallen",
            CONF_TITLE: "Kritieke fout",
        })

        assert self.manager.alerts[0]["title"] == "Kritieke fout"

    def test_create_alert_sets_repeat_interval_in_seconds(self):
        """repeat_interval is stored in seconds (input is in minutes)."""
        self.manager.create_alert({
            CONF_ALERT_TYPE: "info",
            CONF_MESSAGE: "Herhaal test",
            CONF_REPEAT_INTERVAL: 5,  # 5 minutes
        })

        alert = self.manager.alerts[0]
        assert alert["repeat_interval"] == 300  # 5 * 60
        assert alert["next_repeat"] is not None

    def test_create_alert_without_repeat_has_no_next_repeat(self):
        """An alert without repeat_interval has no next_repeat."""
        self.manager.create_alert({
            CONF_ALERT_TYPE: "success",
            CONF_MESSAGE: "Geen herhaling",
        })

        assert self.manager.alerts[0]["next_repeat"] is None

    def test_create_multiple_alerts(self):
        """Multiple alerts can be created independently."""
        self.manager.create_alert({CONF_ALERT_TYPE: "error", CONF_MESSAGE: "Alert 1"})
        self.manager.create_alert({CONF_ALERT_TYPE: "warning", CONF_MESSAGE: "Alert 2"})
        self.manager.create_alert({CONF_ALERT_TYPE: "info", CONF_MESSAGE: "Alert 3"})

        assert len(self.manager.alerts) == 3

    def test_create_alert_notifies_listeners(self):
        """Creating an alert calls all registered listeners."""
        listener = MagicMock()
        self.manager.add_listener(listener)

        self.manager.create_alert({CONF_ALERT_TYPE: "info", CONF_MESSAGE: "Test"})

        listener.assert_called_once()

    def test_create_alert_with_condition_sets_up_listener(self):
        """An alert with condition_entity registers a state change listener."""
        with patch(
            "custom_components.ha_alert.async_track_state_change_event",
            return_value=MagicMock()
        ) as mock_track:
            self.manager.create_alert({
                CONF_ALERT_TYPE: "warning",
                CONF_MESSAGE: "Raam open",
                CONF_CONDITION_ENTITY: "binary_sensor.raam",
                CONF_CONDITION_STATE: "off",
            })

            mock_track.assert_called_once()


# ---------------------------------------------------------------------------
# HAAlertManager — dismiss_alert
# ---------------------------------------------------------------------------

class TestDismissAlert:
    """Tests for HAAlertManager.dismiss_alert."""

    def setup_method(self):
        self.hass = MagicMock()
        self.manager = HAAlertManager(self.hass)

    def test_dismiss_existing_alert(self):
        """Dismissing an existing alert removes it."""
        alert_id = self.manager.create_alert({
            CONF_ALERT_TYPE: "warning",
            CONF_MESSAGE: "Te verwijderen",
        })

        result = self.manager.dismiss_alert(alert_id)

        assert result is True
        assert len(self.manager.alerts) == 0

    def test_dismiss_nonexistent_alert(self):
        """Dismissing a non-existent alert returns False."""
        result = self.manager.dismiss_alert("alert_niet_bestaand")

        assert result is False

    def test_dismiss_notifies_listeners(self):
        """Dismissing an alert calls all registered listeners."""
        alert_id = self.manager.create_alert({
            CONF_ALERT_TYPE: "info",
            CONF_MESSAGE: "Test",
        })
        listener = MagicMock()
        self.manager.add_listener(listener)

        self.manager.dismiss_alert(alert_id)

        listener.assert_called_once()

    def test_dismiss_cleans_up_condition_listener(self):
        """Dismissing an alert with a condition cleans up the state listener."""
        unsub_mock = MagicMock()
        with patch(
            "custom_components.ha_alert.async_track_state_change_event",
            return_value=unsub_mock
        ):
            alert_id = self.manager.create_alert({
                CONF_ALERT_TYPE: "warning",
                CONF_MESSAGE: "Met conditie",
                CONF_CONDITION_ENTITY: "binary_sensor.test",
                CONF_CONDITION_STATE: "off",
            })

            self.manager.dismiss_alert(alert_id)

            unsub_mock.assert_called_once()


# ---------------------------------------------------------------------------
# HAAlertManager — acknowledge_alert
# ---------------------------------------------------------------------------

class TestAcknowledgeAlert:
    """Tests for HAAlertManager.acknowledge_alert."""

    def setup_method(self):
        self.hass = MagicMock()
        self.manager = HAAlertManager(self.hass)

    def test_acknowledge_existing_alert(self):
        """Acknowledging an alert sets acknowledged to True."""
        alert_id = self.manager.create_alert({
            CONF_ALERT_TYPE: "error",
            CONF_MESSAGE: "Test",
        })

        result = self.manager.acknowledge_alert(alert_id)

        assert result is True
        assert self.manager.alerts[0]["acknowledged"] is True
        assert self.manager.alerts[0]["acknowledged_at"] is not None

    def test_acknowledge_nonexistent_alert(self):
        """Acknowledging a non-existent alert returns False."""
        result = self.manager.acknowledge_alert("alert_niet_bestaand")

        assert result is False

    def test_acknowledge_notifies_listeners(self):
        """Acknowledging an alert calls all registered listeners."""
        alert_id = self.manager.create_alert({
            CONF_ALERT_TYPE: "info",
            CONF_MESSAGE: "Test",
        })
        listener = MagicMock()
        self.manager.add_listener(listener)

        self.manager.acknowledge_alert(alert_id)

        listener.assert_called_once()


# ---------------------------------------------------------------------------
# HAAlertManager — repeat logic
# ---------------------------------------------------------------------------

class TestRepeatLogic:
    """Tests for HAAlertManager repeat functionality."""

    def setup_method(self):
        self.hass = MagicMock()
        self.manager = HAAlertManager(self.hass)

    @pytest.mark.asyncio
    async def test_repeat_resets_acknowledged(self):
        """When repeat fires, acknowledged is reset to False."""
        alert_id = self.manager.create_alert({
            CONF_ALERT_TYPE: "warning",
            CONF_MESSAGE: "Herhaal mij",
            CONF_REPEAT_INTERVAL: 1,  # 1 minute = 60 seconds internally
        })

        # Acknowledge it
        self.manager.acknowledge_alert(alert_id)
        assert self.manager.alerts[0]["acknowledged"] is True

        # Force next_repeat to the past
        self.manager._alerts[alert_id]["next_repeat"] = 0

        await self.manager.async_check_repeats()

        assert self.manager.alerts[0]["acknowledged"] is False

    @pytest.mark.asyncio
    async def test_no_repeat_when_not_due(self):
        """Repeat does not fire when next_repeat is in the future."""
        alert_id = self.manager.create_alert({
            CONF_ALERT_TYPE: "info",
            CONF_MESSAGE: "Nog niet",
            CONF_REPEAT_INTERVAL: 60,  # 60 minutes
        })

        self.manager.acknowledge_alert(alert_id)
        # next_repeat is in the future, so no reset
        await self.manager.async_check_repeats()

        assert self.manager.alerts[0]["acknowledged"] is True

    @pytest.mark.asyncio
    async def test_repeat_stops_after_repeat_until(self):
        """Repeat does not fire after repeat_until has passed."""
        alert_id = self.manager.create_alert({
            CONF_ALERT_TYPE: "warning",
            CONF_MESSAGE: "Verlopen",
            CONF_REPEAT_INTERVAL: 1,
            CONF_REPEAT_UNTIL: "2000-01-01T00:00:00",  # ver in het verleden
        })

        self.manager.acknowledge_alert(alert_id)
        self.manager._alerts[alert_id]["next_repeat"] = 0

        await self.manager.async_check_repeats()

        # acknowledged should still be True because repeat_until has passed
        assert self.manager.alerts[0]["acknowledged"] is True


# ---------------------------------------------------------------------------
# HAAlertManager — listeners
# ---------------------------------------------------------------------------

class TestListeners:
    """Tests for HAAlertManager listener management."""

    def setup_method(self):
        self.hass = MagicMock()
        self.manager = HAAlertManager(self.hass)

    def test_add_and_notify_listener(self):
        """Added listeners are called on notify."""
        listener = MagicMock()
        self.manager.add_listener(listener)
        self.manager._notify_listeners()

        listener.assert_called_once()

    def test_remove_listener(self):
        """Removed listeners are no longer called."""
        listener = MagicMock()
        self.manager.add_listener(listener)
        self.manager.remove_listener(listener)
        self.manager._notify_listeners()

        listener.assert_not_called()

    def test_failing_listener_does_not_crash(self):
        """A listener that raises an exception does not crash the manager."""
        def bad_listener():
            raise RuntimeError("Listener fout")

        self.manager.add_listener(bad_listener)
        # Should not raise
        self.manager._notify_listeners()


# ---------------------------------------------------------------------------
# HAAlertManager — stop
# ---------------------------------------------------------------------------

class TestStop:
    """Tests for HAAlertManager.stop."""

    def setup_method(self):
        self.hass = MagicMock()
        self.manager = HAAlertManager(self.hass)

    def test_stop_cancels_repeat_task(self):
        """stop() cancels the repeat task if it exists."""
        mock_task = MagicMock()
        self.manager._repeat_task = mock_task

        self.manager.stop()

        mock_task.cancel.assert_called_once()

    def test_stop_cleans_up_condition_listeners(self):
        """stop() calls all condition listener unsubscribes."""
        unsub1 = MagicMock()
        unsub2 = MagicMock()
        self.manager._state_unsubs = {"alert_1": unsub1, "alert_2": unsub2}

        self.manager.stop()

        unsub1.assert_called_once()
        unsub2.assert_called_once()
        assert len(self.manager._state_unsubs) == 0
