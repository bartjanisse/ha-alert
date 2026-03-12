"""Tests for HA Alert config_flow.py."""
from __future__ import annotations

import pytest
from unittest.mock import AsyncMock, MagicMock, patch


class TestConfigFlow:
    """Tests for HAAlertConfigFlow."""

    def _get_flow(self, hass):
        """Return a configured config flow instance."""
        from custom_components.ha_alert.config_flow import HAAlertConfigFlow
        flow = HAAlertConfigFlow()
        flow.hass = hass
        flow.context = {"source": "user"}
        flow._async_abort_entries_match = MagicMock(return_value=None)
        return flow

    @pytest.mark.asyncio
    async def test_show_form_on_first_call(self):
        """Config flow shows a form when called without user input."""
        hass = MagicMock()
        flow = self._get_flow(hass)

        with patch.object(flow, "async_set_unique_id", new=AsyncMock()), \
             patch.object(flow, "_abort_if_unique_id_configured", return_value=None):
            result = await flow.async_step_user(user_input=None)

        assert result["type"] == "form"
        assert result["step_id"] == "user"

    @pytest.mark.asyncio
    async def test_creates_entry_on_submit(self):
        """Config flow creates an entry when user submits the form."""
        hass = MagicMock()
        flow = self._get_flow(hass)

        with patch.object(flow, "async_set_unique_id", new=AsyncMock()), \
             patch.object(flow, "_abort_if_unique_id_configured", return_value=None), \
             patch.object(flow, "async_create_entry", return_value={"type": "create_entry", "title": "HA Alert", "data": {}}) as mock_create:
            result = await flow.async_step_user(user_input={})

        mock_create.assert_called_once_with(title="HA Alert", data={})

    @pytest.mark.asyncio
    async def test_aborts_if_already_configured(self):
        """Config flow aborts when integration is already configured."""
        hass = MagicMock()
        flow = self._get_flow(hass)

        with patch.object(flow, "async_set_unique_id", new=AsyncMock()), \
             patch.object(flow, "_abort_if_unique_id_configured", side_effect=Exception("already_configured")):
            with pytest.raises(Exception, match="already_configured"):
                await flow.async_step_user(user_input=None)
