# Personal Configs
STOP_IDS = ["A17"]
ROUTES = set({"1", "2", "3", "A", "C", "B", "D"})
STATION_MINIMUM_MINUTES_DISPLAY = {
    "A17": 1,
    "118": 10,
    "227": 9,
}
DIRECTIONS = ["S", "N"] # Options: "S", "N"
# Hardware configs
UPDATE_DELAY = 10  # in seconds
SYNC_TIME_DELAY = 60
RESET_DELAY = 3600 # CircuitPython runs out of sockets occasionally. Reset it periodically.
ERROR_RESET_THRESHOLD = 30