import gc
import network
from time import sleep, ticks_ms
import urequests as reqs
import utime
import ujson
from galactic import GalacticUnicorn, Channel
from picographics import PicoGraphics, DISPLAY_GALACTIC_UNICORN

gu = GalacticUnicorn()
graphics = PicoGraphics(DISPLAY_GALACTIC_UNICORN)

width = GalacticUnicorn.WIDTH
height = GalacticUnicorn.HEIGHT

BACKGROUND_COLOR = (0, 0, 0)  # Black
COMMIT_COLOR = (30, 200, 30)  # Green

# REPLACE THE FOLLOWING WITH YOUR OWN INFORMATION
WIFI_SSID = "YOUR_WIFI_SSID"
WIFI_PASSWORD = "YOUR_WIFI_PASSWORD"
GITHUB_USERNAME = "YOUR_GITHUB_USERNAME"
GITHUB_TOKEN = "YOUR GITHUB TOKEN"

REFRESH_INTERVAL_SECONDS = 30


def connect():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(WIFI_SSID, WIFI_PASSWORD)
    while wlan.isconnected() == False:
        print('Waiting for connection...')
        sleep(1)
    ip = wlan.ifconfig()[0]
    print(f'Connected on {ip}')


class github_matrix():
    def __init__(self):
        # Data
        self.pixel_data = None
        self.calendar = None
        self.response = None

        # History
        self.max_contributions = 0
        self.min_contributions = float('inf')
        self.contributions_today = None

        # Display preferances
        self.mode = "ONE_COLOR"
        self.gradient_array = None

        # Status
        self.is_calendar_loaded = False

        # Start first workflow on start up
        self.workflow()

    def workflow(self):
        self.get_github_content()
        self.parse_calendar_json()
        self.calculate_week_pixels()
        self.check_for_activity_change()
        self.paint_by_mode()

    def get_github_content(self):
        # Due to memory restrictions, it's necessary todelete previous calendar data in order to free memory needed for parsing
        # the response.
        self.calendar = None
        self.pixel_data = None
        self.is_calendar_loaded = False
        self.response = None
        gc.collect()
        gh_url = f'https://api.github.com/graphql'
        headers = {
            "User-Agent": "Galactic-Unicorn-Github-Calendar",
            "Authorization": f"bearer {GITHUB_TOKEN}"
        }

        query = (
                "{\n"
                "  user(login: \"" + GITHUB_USERNAME + "\") {\n"
                                                       "    contributionsCollection {\n"
                                                       "      contributionCalendar {\n"
                                                       "        weeks {\n"
                                                       "          contributionDays {\n"
                                                       "            color\n"
                                                       "            contributionCount\n"
                                                       "            date\n"
                                                       "          }\n"
                                                       "        }\n"
                                                       "      }\n"
                                                       "    }\n"
                                                       "  }\n"
                                                       "}\n"
        )
        res = reqs.post(gh_url, json={"query": query}, headers=headers)
        gc.collect()
        parsedJson = ujson.load(res.raw)
        res.close()
        del res
        gc.collect()
        self.response = parsedJson

    def parse_calendar_json(self):
        if self.response is None:
            raise Exception("In parse_calendar_json: Response is not loaded")
        else:
            pass
        activityJSON = self.response
        parsedCalendar = activityJSON["data"]["user"]["contributionsCollection"]["contributionCalendar"]["weeks"]
        self.calendar = parsedCalendar

    def check_for_activity_change(self):
        last_column = self.pixel_data[len(self.pixel_data) - 1]
        last_entry = last_column[len(last_column) - 1]
        latest_date = last_entry["date"]
        latest_contribution_count = last_entry["contributionCount"]

        if self.contributions_today != None:
            if (latest_contribution_count > self.contributions_today):
                self.handle_new_contribution()

        self.contributions_today = latest_contribution_count

    def handle_new_contribution(self):
        self.strobe_message()

    def strobe_message(self):
        message_start_time = utime.time()
        message_done = False
        graphics.set_font("bitmap8")
        while message_done == False:
            graphics.set_pen(graphics.create_pen(0, 0, 0))
            graphics.rectangle(0, 0, width, height)
            graphics.set_pen(graphics.create_pen(*COMMIT_COLOR))
            graphics.text("NEW COMMIT", 2, 2, 10000, 0.3)
            gu.update(graphics)
            sleep(1)
            graphics.set_pen(graphics.create_pen(0, 0, 0))
            graphics.rectangle(0, 0, width, height)
            gu.update(graphics)

            sleep(1)

            message_current_time = utime.time()
            elapsed = message_current_time - message_start_time
            if elapsed > 10:
                message_done = True

    def calculate_week_pixels(self):
        if self.calendar is None:
            raise Exception("In calculate_week_pixels: Calendar is not loaded")
        else:
            pass
        weeks = self.calendar
        pixel_column_array = []
        for week in weeks:
            column = []
            days = week["contributionDays"]
            for day in days:
                contribution_count = day["contributionCount"]
                date = day["date"]
                if contribution_count > self.max_contributions:
                    self.max_contributions = contribution_count
                if contribution_count < self.min_contributions:
                    self.min_contributions = contribution_count
                column.append({
                    "color": day["color"],
                    "contributionCount": contribution_count,
                    "date": date
                })
            pixel_column_array.append(column)
        self.pixel_data = pixel_column_array

    def paint_by_mode(self):
        mode_name = self.mode
        if (mode_name == "GRADIENT" and self.gradient_array is not None):
            self.draw_pixel_array_rainbow(self.gradient_array)
        elif (mode_name == "ONE_COLOR"):
            self.draw_pixel_array()

    def change_mode(self, mode_name, new_gradient_array=None):
        if (self.mode == mode_name and new_gradient_array == self.gradient_array):
            return
        self.mode = mode_name
        self.gradient_array = new_gradient_array
        self.paint_by_mode()

    def draw_pixel_array_rainbow(self, gradient_colors):
        if self.calendar is None:
            raise Exception("In draw_pixel_array: Calendar is not loaded")
        else:
            pass

        background = graphics.create_pen(*BACKGROUND_COLOR)
        num_colors = len(gradient_colors)
        num_steps_per_transition = 372 // (num_colors - 1)
        step = 1
        pixels_column_array = self.pixel_data
        column = 0
        for week_column in pixels_column_array:
            row = 2
            for day in week_column:
                color = self.hex_to_rgb(day["color"])
                luminance = self.calculate_rgb_luminance(*color)
                brightness_factor = 1.0 - luminance / 255.0
                color_index = step // num_steps_per_transition
                color_index1 = min(color_index, num_colors - 1)
                color_index2 = min(color_index1 + 1, num_colors - 1)
                sub_step = step % num_steps_per_transition
                sub_factor = sub_step / num_steps_per_transition
                interpolated_color = self.interpolate_color(gradient_colors[color_index1],
                                                            gradient_colors[color_index2], sub_factor)
                dimmed = self.dim_color(interpolated_color, brightness_factor)
                # Set color to black if color match's github's color for 0 contributions
                if (color == (235, 237, 240)):
                    graphics.set_pen(background)
                else:
                    graphics.set_pen(graphics.create_pen(*dimmed))
                graphics.pixel(column, row)
                gu.update(graphics)
                row += 1
                step += 1
            column += 1
        gu.update(graphics)
        self.is_calendar_loaded = True
        gc.collect()

    def draw_pixel_array(self):
        if self.calendar is None:
            raise Exception("In calculate_week_pixels: Calendar is not loaded")
        else:
            pass
        background = graphics.create_pen(*BACKGROUND_COLOR)
        pixels_column_array = self.pixel_data
        column = 0
        for week_column in pixels_column_array:
            row = 2
            for day in week_column:
                color = self.hex_to_rgb(day["color"])
                luminance = self.calculate_rgb_luminance(*color)
                brightness_factor = 1.0 - luminance / 255.0
                commit = COMMIT_COLOR
                dimmed_commit = self.dim_color(commit, brightness_factor)
                # Set color to black if color match's github's color for 0 contributions
                if (color == (235, 237, 240)):
                    graphics.set_pen(background)
                else:
                    graphics.set_pen(graphics.create_pen(*dimmed_commit))
                graphics.pixel(column, row)
                gu.update(graphics)
                row += 1
            column += 1
        gu.update(graphics)
        self.is_calendar_loaded = True
        gc.collect()

    ####################################
    #
    # Color utilities
    #
    ####################################

    def hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        return (r, g, b)

    def interpolate_color(self, color1, color2, factor):
        r = int(color1[0] + (color2[0] - color1[0]) * factor)
        g = int(color1[1] + (color2[1] - color1[1]) * factor)
        b = int(color1[2] + (color2[2] - color1[2]) * factor)
        return (r, g, b)

    def calculate_rgb_luminance(self, r, g, b):
        return 0.2126 * r + 0.715 * g + 0.0722 * b

    def dim_color(self, rgb_tuple, factor):
        r, g, b = rgb_tuple
        dim_r = int(r * factor)
        dim_g = int(g * factor)
        dim_b = int(b * factor)
        return dim_r, dim_g, dim_b


# Connect to wifi
connect()

matrix = github_matrix()

# Start timer
start_time = utime.time()
while matrix.is_calendar_loaded == True:

    # Ping for data every 60 seconds
    current_time = utime.time()
    elapsed_time = current_time - start_time
    if (elapsed_time != 0 and elapsed_time % REFRESH_INTERVAL_SECONDS == 0):
        matrix.workflow()

    if gu.is_pressed(GalacticUnicorn.SWITCH_A):
        matrix.change_mode("ONE_COLOR")

    if gu.is_pressed(GalacticUnicorn.SWITCH_B):
        matrix.change_mode("GRADIENT", [
            (255, 100, 100),  # Pink
            (40, 0, 255),  # Blue
        ])

    if gu.is_pressed(GalacticUnicorn.SWITCH_C):
        matrix.change_mode("GRADIENT", [
            (255, 0, 0),  # Red
            (255, 165, 0),  # Orange
            (255, 255, 0),  # Yellow
            (0, 255, 0),  # Green
            (0, 0, 255),  # Blue
        ])

    if gu.is_pressed(GalacticUnicorn.SWITCH_D):
        sleep(0.3)
        # Hold down D and C in succession to refresh
        if gu.is_pressed(GalacticUnicorn.SWITCH_C):
            del matrix
            gc.collect()
            matrix = github_matrix()
    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_UP):
        gu.adjust_brightness(+0.01)
        gu.update(graphics)
        sleep(0.01)

    if gu.is_pressed(GalacticUnicorn.SWITCH_BRIGHTNESS_DOWN):
        gu.adjust_brightness(-0.01)
        gu.update(graphics)
        sleep(0.01)

    if gu.is_pressed(GalacticUnicorn.SWITCH_VOLUME_UP):
        gu.set_volume(+0.1)
        sleep(0.01)

    if gu.is_pressed(GalacticUnicorn.SWITCH_VOLUME_DOWN):
        gu.set_volume(-0.1)
        sleep(0.01)

