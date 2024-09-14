import time

import microcontroller
from board import NEOPIXEL
import displayio
import gc
import adafruit_display_text.label
from adafruit_datetime import datetime
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.matrix import Matrix
from adafruit_matrixportal.network import Network

import configs
import constants
import train

def fetch_data(stop_ids):
    try:
        query = constants.DATA_URL + ",".join(stop_ids)
        data = network.fetch_data(
            query, json_path=(constants.DATA_LOCATION,)
        )
        return data
    except MemoryError as e:
        gc.collect()
        print("Some error occured: ", e)

def get_arrival_in_minutes_from_now(now, date_str):
    # Remove tzinfo to diff dates
    train_date = datetime.fromisoformat(date_str).replace(tzinfo=None)
    return round((train_date - now).total_seconds() / 60.0)

# Get soonest trains at a given station
# Input direction (e.g. "N", "S")
# Return list of Train objects
def get_trains_for_station(station_data, direction):
    now = datetime.now()
    print("Now: ", now)
    station_id = station_data["id"]
    print("Station ID: ", station_id)
    # Create list of Train objects for each train arriving at station
    trains = []
    trains = [
        train.Train(
            x["route"],
            get_arrival_in_minutes_from_now(now, x["time"]),
            station_id,
            direction,
        )
        for x in station_data[direction]
    ]

    # Filter by arrival time and route
    arrivals = []
    for arriving_train in trains:
        if (
            arriving_train.num_minutes >= arriving_train.station_minutes_minimum_display
            and arriving_train.route in configs.ROUTES
        ):
            arrivals.append(arriving_train)
    return arrivals

def get_trains(direction):
    gc.collect()
    all_trains = []
    train_data = fetch_data(configs.STOP_IDS)
    for station_data in train_data:
        all_trains = all_trains + get_trains_for_station(station_data, direction)
    all_trains.sort(key=lambda x: x.num_minutes, reverse=False)
    return all_trains[0:3]

def update_text(trains):
    if len(trains) < 3:
        for i in range(3, len(trains), -1):
            text_lines[i].text = constants.NULL_DATA
            text_lines[i].color = constants.NULL_DATA_COLOR
    line = 1
    for train in trains:
        text_lines[line].text = "%s  %s   %sm" % (
            train.route,
            train.direction_label,
            train.num_minutes,
        )
        text_lines[line].color = train.route_color
        line += 1
    display.root_group = group


# --- Display setup ---
matrix = Matrix()
display = matrix.display
network = Network(status_neopixel=NEOPIXEL, debug=False)

# --- Drawing setup ---
group = displayio.Group()
font = bitmap_font.load_font("fonts/6x10.bdf")
text_lines = [
    adafruit_display_text.label.Label(
        font, color=constants.HEADER_COLOR, x=3, y=3, text="LN DIR MIN"
    ),
    adafruit_display_text.label.Label(
        font, color=constants.NULL_DATA_COLOR, x=3, y=11, text=constants.NULL_DATA
    ),
    adafruit_display_text.label.Label(
        font, color=constants.NULL_DATA_COLOR, x=3, y=20, text=constants.NULL_DATA
    ),
    adafruit_display_text.label.Label(
        font, color=constants.NULL_DATA_COLOR, x=3, y=28, text=constants.NULL_DATA
    ),
]
for x in text_lines:
    group.append(x)
display.root_group = group


# --- Main loop ---
last_reset = time.monotonic()
last_time_sync = None
it_dir = 0
while True:
    try:
        if (time.monotonic() > last_reset + configs.RESET_DELAY):
            microcontroller.reset()
        if (
            last_time_sync is None
            or time.monotonic() > last_time_sync + configs.SYNC_TIME_DELAY
        ):
            # Sync clock to minimize time drift
            network.get_local_time()
            last_time_sync = time.monotonic()
        arrivals = [get_trains(configs.DIRECTIONS[it_dir])]
        update_text(*arrivals)
    except (ValueError, RuntimeError) as e:
        print("Some error occured, retrying! -", e)

    it_dir = (it_dir + 1) % len(configs.DIRECTIONS)
    time.sleep(configs.UPDATE_DELAY)
