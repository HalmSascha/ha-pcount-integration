"""Constants for the p-count integration."""

DOMAIN = "pcount"

CONF_CARPARK_ID = "carpark_id"
CONF_SCAN_INTERVAL = "scan_interval"

DEFAULT_HOST = "p-count.de"

# The update/poll interval is user-configurable via the options flow, but
# must never go below this floor - defaults to it as well.
DEFAULT_SCAN_INTERVAL = 30
MIN_SCAN_INTERVAL = 30
