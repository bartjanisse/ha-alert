"""Constants for the HA Alert integration."""

DOMAIN = "ha_alert"

CONF_ALERT_TYPE = "alert_type"
CONF_MESSAGE = "message"
CONF_TITLE = "title"
CONF_ENTITY_ID = "entity_id"
CONF_REPEAT_INTERVAL = "repeat_interval"
CONF_REPEAT_UNTIL = "repeat_until"
CONF_CONDITION_ENTITY = "condition_entity"
CONF_CONDITION_STATE = "condition_state"

ALERT_TYPE_ERROR = "error"
ALERT_TYPE_WARNING = "warning"
ALERT_TYPE_INFO = "info"
ALERT_TYPE_SUCCESS = "success"

ALERT_TYPES = [ALERT_TYPE_ERROR, ALERT_TYPE_WARNING, ALERT_TYPE_INFO, ALERT_TYPE_SUCCESS]

SERVICE_CREATE = "create"
SERVICE_DISMISS = "dismiss"
SERVICE_ACKNOWLEDGE = "acknowledge"

ATTR_ALERTS = "alerts"
ATTR_LAST_UPDATED = "last_updated"

SENSOR_ACTIVE_ALERTS = "active_alerts"
