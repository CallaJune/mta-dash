import configs
import constants


class Train:
    def __init__(self, route, num_minutes, station_id, direction):
        self.route = route
        self.num_minutes = num_minutes
        self.station_id = station_id
        self.station_name = constants.STATION_LABELS[station_id]
        if route in constants.ROUTE_COLORS:
            self.route_color = constants.ROUTE_COLORS[route]
        else:
            self.route_color = 0xFFFFFF
        self.station_minutes_minimum_display = configs.STATION_MINIMUM_MINUTES_DISPLAY[
            station_id
        ]
        self.direction = direction
        self.direction_label = constants.DIRECTION_LABELS[direction]
