import time
import datetime
import os
import pygame
from rive import RiveFile
from radio import start_radio, stop_radio

# --------------------
# CONFIG
# --------------------
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 480
ALARM_HOUR = 7
ALARM_MINUTE = 30

RADIO_STATIONS = [
    ("BBC Radio 4", "http://stream.live.vc.bbcmedia.co.uk/bbc_radio_fourfm"),
    ("BBC Radio 6 Music", "http://stream.live.vc.bbcmedia.co.uk/bbc_6music"),
    ("BBC Radio 1", "http://stream.live.vc.bbcmedia.co.uk/bbc_radio_one"),
]

# --------------------
# ENVIRONMENT
# --------------------
CI = os.environ.get("CI") == "true"

if CI:
    import gpio_mock as gpio
else:
    import gpio

# --------------------
# PYGAME SETUP
# --------------------
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

# --------------------
# LOAD RIVE
# --------------------
rive = RiveFile("clock.riv")
artboard = rive.default_artboard
machine = artboard.state_machine("ClockMachine")

alarm_on = machine.input("alarm_on")
station_index_input = machine.input("station_index")
station_confirmed_input = machine.input("station_confirmed")

# --------------------
# STATE
# --------------------
station_index = 0
alarm_triggered = False
radio_process = None

# --------------------
# MAIN LOOP
# --------------------
running = True
while running:
    dt = clock.tick(60) / 1000.0
    now = datetime.datetime.now()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if alarm_triggered:
                alarm_on.value = False
                stop_radio(radio_process)
                radio_process = None
                alarm_triggered = False

    # Alarm check
    if (
        now.hour == ALARM_HOUR
        and now.minute == ALARM_MINUTE
        and not alarm_triggered
    ):
        alarm_triggered = True
        alarm_on.value = True
        _, url = RADIO_STATIONS[station_index]
        radio_process = start_radio(url)

    # Update Rive
    machine.advance(dt)
    artboard.advance(dt)

    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    artboard.draw(surface)
    screen.blit(surface, (0, 0))
    pygame.display.flip()

pygame.quit()

