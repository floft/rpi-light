#!/usr/bin/env python3
"""
Turn on/off lights via setting serial port high/low
"""
import time
import serial
import argparse

class Lights:
    """
    Turn on/off lights via serial

    Usage:
        s = Serial("/dev/ttyUSB0")
        s.on()
        time.sleep(3)
        s.off()
    """
    def __init__(self, port, **kwargs):
        self.port = port
        self.serial = serial.Serial(port, **kwargs)

    def on(self):
        self.serial.setRTS(True)

    def off(self):
        self.serial.setRTS(False)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--port', default="/dev/ttyUSB0", type=str,
        help="Full path to the serial port (default /dev/ttyUSB0)")
    args = parser.parse_args()

    l = Lights(args.port)

    while True:
        print("Lights on")
        l.on()
        time.sleep(3)
        print("Lights off")
        l.off()
        time.sleep(3)
