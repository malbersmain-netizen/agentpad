"""Milestone 6 smoke test: prove Python can drive the board and read buttons."""
import serial, time

PORT = "/dev/cu.usbserial-0001"   # confirmed on this build

ser = serial.Serial(PORT, 115200, timeout=0.1)
time.sleep(2)          # the ESP32 reboots when the port opens

ser.write(b"D0 hello from python\n")
ser.write(b"D1 press a button\n")
ser.write(b"L 0 blocked\n")

print("driving board. press buttons (Ctrl-C to quit)...")
while True:
    line = ser.readline().decode(errors="ignore").strip()
    if line:
        print(line)
