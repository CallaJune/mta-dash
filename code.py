import time

import microcontroller
from board import NEOPIXEL
import displayio
import gc
from adafruit_display_text import label
from adafruit_datetime import datetime
from adafruit_bitmap_font import bitmap_font
from adafruit_matrixportal.matrix import Matrix
from adafruit_matrixportal.network import Network
from adafruit_display_shapes import circle

import configs
import constants
import train

def fetch_train_data(stop_ids):
    try:
        query = constants.DATA_URL + ",".join(stop_ids)
        data = network.fetch_data(
            query, json_path=(constants.DATA_LOCATION,)
        )
        return data
    except Exception as e:
        print("Some error occured in fetch_data(): ", e)
        handle_errors()

def get_arrival_in_minutes_from_now(now, date_str):
    # Remove tzinfo to diff dates
    arrival_date = datetime.fromisoformat(date_str).replace(tzinfo=None)
    return round((arrival_date - now).total_seconds() / 60.0)

# Get soonest trains at a given station
# Input direction (e.g. "N", "S")
# Return list of Train objects
def get_trains_for_station(station_data, direction):
    now = datetime.now()
    station_id = station_data["id"]
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
    train_data = fetch_train_data(configs.STOP_IDS)
    if train_data:
        for station_data in train_data:
            all_trains = all_trains + get_trains_for_station(station_data, direction)
        all_trains.sort(key=lambda x: x.num_minutes, reverse=False)
    return all_trains[0:3]

def update_text(trains):
    if len(trains) < 3:
        for i in range(2, len(trains) - 1, -1):
            train_lines[i][0].fill = constants.BACKGROUND_COLOR
            train_lines[i][2].color = constants.NULL_DATA_COLOR
            train_lines[i][1].color = constants.NULL_DATA_COLOR
            train_lines[i][1].text = "-"
            train_lines[i][2].text = constants.NULL_DATA

    line = 0
    for train in trains:
        train_lines[line][0].fill = train.route_color
        train_lines[line][2].color = train.route_color
        train_lines[line][1].color = constants.BACKGROUND_COLOR
        train_lines[line][1].text = train.route
        train_lines[line][2].text = "   %s   %sm" % (
            train.direction_label,
            train.num_minutes,
        )
        line += 1
    display.root_group = group

def handle_errors():
    global error_counter
    error_counter += 1
    gc.collect()
    print("Error counter: ", error_counter)
    if error_counter > configs.ERROR_RESET_THRESHOLD:
        microcontroller.reset()


# --- Display setup ---
matrix = Matrix()
display = matrix.display
network = Network(status_neopixel=NEOPIXEL, debug=False)

# --- Drawing setup ---
group = displayio.Group()
primary_font = bitmap_font.load_font("fonts/6x10.bdf")
thumbnail_font = bitmap_font.load_font("fonts/tom-thumb.bdf")
header = [
    label.Label(
        primary_font, color=constants.HEADER_COLOR, x=3, y=3, text="LN DIR MIN"
    ),
]
train_lines = [
    (
        circle.Circle(fill=constants.BACKGROUND_COLOR, x0=5, y0=11, r=3), 
        label.Label(thumbnail_font, color=constants.NULL_DATA_COLOR, x=4, y=12, text="-"),
        label.Label(primary_font, color=constants.NULL_DATA_COLOR, x=3, y=11, text=constants.NULL_DATA)
    ),
    (
        circle.Circle(fill=constants.BACKGROUND_COLOR, x0=5, y0=20, r=3),
        label.Label(thumbnail_font, color=constants.NULL_DATA_COLOR, x=4, y=21, text="-"),
        label.Label(primary_font, color=constants.NULL_DATA_COLOR, x=3, y=20, text=constants.NULL_DATA)
    ),
    (
        circle.Circle(fill=constants.BACKGROUND_COLOR, x0=5, y0=28, r=3),
        label.Label(thumbnail_font, color=constants.NULL_DATA_COLOR, x=4, y=29, text="-"),
        label.Label(primary_font, color=constants.NULL_DATA_COLOR, x=3, y=28, text=constants.NULL_DATA)
    )
]

group.append(header[0])
for x in train_lines:
    group.append(x[0])
    group.append(x[1])
    group.append(x[2])
display.root_group = group


# --- Main loop ---
last_reset = time.monotonic()
last_time_sync = None
it_dir = 0
error_counter = 0
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
    except Exception as e:
        print("Some error occured in main loop: ", e)
        handle_errors()

    it_dir = (it_dir + 1) % len(configs.DIRECTIONS)
    time.sleep(configs.UPDATE_DELAY)
