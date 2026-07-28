"""Milestone 8: controller button discovery.

Run this, press every button, and write down which number each one reports.
Cheap USB adapters number buttons unpredictably, so we measure instead of guess.
The d-pad usually shows up as `hat` values like (0, 1) rather than buttons.
pygame may open a small blank window -- that's normal, leave it open.
"""
import pygame

pygame.init()
pygame.joystick.init()
if pygame.joystick.get_count() == 0:
    raise SystemExit("No controller found. Plug it into the hub and try again.")
js = pygame.joystick.Joystick(0)
js.init()
print("pad:", js.get_name())
print("press every button / direction. Ctrl-C to quit.\n")

while True:
    for e in pygame.event.get():
        if e.type == pygame.JOYBUTTONDOWN:
            print("button", e.button)
        elif e.type == pygame.JOYHATMOTION:
            print("hat", e.value)
        elif e.type == pygame.JOYAXISMOTION and abs(e.value) > 0.5:
            print("axis", e.axis, round(e.value, 2))
