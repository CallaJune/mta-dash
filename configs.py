# Personal Configs
STOP_IDS = ["601"]
ROUTES = set({"1", "2", "3", "A", "C", "B", "D", "6"})
STATION_MINIMUM_MINUTES_DISPLAY = {
    "A17": 1,
    "118": 10,
    "227": 9,
    "601": 1,
}
DIRECTIONS = ["S", "N"] # Options: "S", "N"
# Hardware configs
UPDATE_DELAY = 10  # in seconds
SYNC_TIME_DELAY = 60 # in seconds; syncs to network time every so often to prevent drift
RESET_DELAY = 7200 # CircuitPython runs out of sockets occasionally. Reset it periodically.
ERROR_RESET_THRESHOLD = 30 # number of caught errors before the board restarts